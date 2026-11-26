#!/usr/bin/env python3
"""Relative re-rating of all exercises (printed set + supplements 1-3).
score = 0.6 * z(previous rating) + 0.4 * z(content features); exercises are ranked on that score and the rank is
mapped to a bell curve: note = 10 + 2.2 * z(percentile), clipped to [5, 15], in steps of 0.5.
usage: python3 tools/rerate.py SCRATCH   -> work/ratings_v2.json, ratings_v2.csv"""
import csv, glob, json, os, re, sys
from statistics import NormalDist, mean, pstdev

S = sys.argv[1]
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rows = list(csv.DictReader(open(os.path.join(HERE, "complet_exercices.csv"), encoding="utf-8")))

# ---- text of every exercise --------------------------------------------------------------
text = {}
seg = json.load(open(S + "/wn2/seg/manifest.json"))
def sid(e):
    f = re.sub(r"_[\w-]{6}$", "", e["file"]).replace("_SC_SC", "_SC").replace("_dvs_dvs", "_dvs").replace("_exo_exo", "_exo").replace("_exo_x", "_exo")
    return "%s_p%dc%dk%d" % (f, e["page"], e["col"], e["k"])
segtxt = {sid(e): e.get("text", "") for e in seg}
for r in json.load(open(os.path.join(HERE, "work", "new_set.json"))):
    text[r["id"]] = segtxt.get(r["src_id"], "")
sup = json.load(open(S + "/suptext.json"))
dv2 = json.load(open(S + "/dv2seg/manifest.json"))
for r in json.load(open(os.path.join(HERE, "work", "sup_set.json"))):
    m = re.match(r"Ex\. (\d+)$", r["label"])
    if m and "#" + m.group(1) in sup and int(r["id"][1:]) < 60:   # D060-D066 are manual crops: no segment text
        text[r["id"]] = sup["#" + m.group(1)]
for r in json.load(open(os.path.join(HERE, "work", "sup2_set.json"))):
    text[r["id"]] = dv2[r["src_index"]].get("text", "")
n = 0
for path in sorted(glob.glob(os.path.join(HERE, "arabe", "*.tex"))):
    for m in re.finditer(r"\\ex\{[^}]*\}\{[^}]*\}\{[^}]*\}\{\d+\}(.*?)\\fin", open(path, encoding="utf8").read(), re.S):
        n += 1
        text["T%03d" % n] = m.group(1)

# ---- content features ----------------------------------------------------------------------
HARD = [r"r[ée]currence|recurrence|par le r[ée]currence|بالترجع", r"\|\s*U.{0,12}[−-].{0,12}\|\s*[≤<]|\\left\|U|\|U_\{?n\+1",
        r"bijection|r[ée]ciproque|f\s*\^?\s*-\s*1|f\^\{-1\}|g\^\{-1\}", r"∑|\\sum|somme|S_n|S\s*n\s*=", r"param[èe]tre|\bm\b.{0,20}r[ée]el|f_m|f m",
        r"E\s*\(|partie enti[èe]re", r"in[ée]galit|≤.{0,40}≤|\\leq.{0,60}\\leq", r"en d[ée]duire|d[ée]duire|déduisez", r"surjecti|injecti",
        r"∘|\\circ|compos[ée]e", r"T_f|T_\{|taux de variation|\\frac\{f\(x\)-f\(y\)\}", r"\(\s*x\s*,\s*y\s*\)|\\mathbb\{R\}\^2|ℝ\s*2|×"]
def features(t):
    if not t.strip():
        return None
    q = len(re.findall(r"\\item|(?<![\w\d])(?:\d|[a-d])\s*\)", t))
    plain = re.sub(r"\\[a-zA-Z]+|[{}$\\^_]", " ", t)
    length = len(plain.split())
    hard = sum(1 for p in HARD if re.search(p, t, re.I))
    return 0.45 * min(q, 14) + 0.012 * min(length, 400) + 0.6 * hard

def z(vals):
    m, s = mean(vals), pstdev(vals) or 1
    return [(v - m) / s for v in vals]

ids = [r["id"] for r in rows]
old = {r["id"]: float(r["difficulty_20"]) for r in rows}
feat = {i: features(text.get(i, "")) for i in ids}
zo = dict(zip(ids, z([old[i] for i in ids])))
have = [i for i in ids if feat[i] is not None]
zf = dict(zip(have, z([feat[i] for i in have])))
score = {i: 0.6 * zo[i] + 0.4 * zf[i] if i in zf else zo[i] for i in ids}

order = sorted(ids, key=lambda i: (score[i], old[i], i))
N, nd = len(order), NormalDist()
new = {}
for k, i in enumerate(order):
    p = (k + 0.5) / N
    v = 10 + 2.2 * nd.inv_cdf(p)
    new[i] = max(5.0, min(15.0, round(v * 2) / 2))

json.dump(new, open(os.path.join(HERE, "work", "ratings_v2.json"), "w"), indent=0)
topic = {r["id"]: r["topic"] for r in rows}
with open(os.path.join(HERE, "ratings_v2.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["id", "topic", "old_difficulty_20", "new_difficulty_20", "rank_easiest_first", "text_features_used"])
    for k, i in enumerate(order, 1):
        w.writerow([i, topic[i], int(old[i]), new[i], k, "yes" if i in zf else "no"])
from collections import Counter
c = Counter(new.values())
print("N", N, "without text:", N - len(zf))
for v in sorted(c):
    print(f"{v:>5}  {c[v]:>3}  {100 * c[v] / N:5.1f}%")
