#!/usr/bin/env python3
"""SUPPLEMENT 2: devoirs du 2e semestre (mathmanti2.webnode.fr, 1ère Bac SM) - only exercises without limits/derivatives.
usage: gen_supplement2.py SCRATCH  (SCRATCH holds dv2seg/ = segment.py output on dv2w/, and /tmp-free p.html copy as page.html)
writes work/ex_sup2/D###.png (ids continue after the first supplement) and work/sup2_set.json."""
import json, os, re, sys, glob, html
from PIL import Image

S = sys.argv[1]
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "work", "ex_sup2"); os.makedirs(OUT, exist_ok=True)
man = json.load(open(S + "/dv2seg/manifest.json"))
START = 67                                   # first supplement uses D001-D066

# Drive id -> (school year, label) from the 2nd-semester "devoirs" list of the page
page = open(S + "/page.html", encoding="utf8").read()
sem2 = page[page.find("2éme semestre"):]; sem2 = sem2[sem2.find(">devoirs<"):]
INFO, year = {}, "?"
for m in re.finditer(r'>(avant2011|\d\d-\d{2,4})<|href="[^"]*drive\.google\.com/(?:file/d/|open\?id=)([\w-]+)[^"]*"[^>]*>(.*?)</a>', sem2, re.S):
    if m.group(1): year = m.group(1)
    else: INFO.setdefault(m.group(2)[:8], (year, html.unescape(re.sub("<[^>]+>", "", m.group(3))).strip() or "devoir", m.group(2)))

SU, E, A = "Suites", "Ensembles", "Applications"
PICK = {10: (SU, 11), 12: (SU, 9), 13: (E, 7), 15: (A, 12), 21: (SU, 12), 23: (SU, 11), 33: (SU, 9), 54: (SU, 13), 60: (SU, 8),
        61: (SU, 13), 69: (SU, 11), 85: (SU, 12), 88: (SU, 11), 106: (SU, 11), 107: (SU, 10), 109: (SU, 9), 110: (SU, 9),
        111: (SU, 12), 127: (SU, 13)}


def stack(ims):
    w = max(i.width for i in ims); o = Image.new("RGB", (w, sum(i.height for i in ims)), "white"); y = 0
    for i in ims: o.paste(i, (0, y)); y += i.height
    return o


def pg(prefix, n):
    return Image.open(glob.glob("%s/dv2seg/_pg_dv2_%s*-%d.png" % (S, prefix, n))[0]).convert("RGB")


rows = []
for n, (j, (t, d)) in enumerate(sorted(PICK.items()), START):
    e = man[j]
    parts = [Image.open(S + "/dv2seg/" + p).convert("RGB") for p in e["parts"]]
    im = stack(parts)
    if j == 10:   im = stack([im, pg("17Yl7kB9", 2).crop((0, 300, 1654, 800))])     # end of the exercise is on page 2 (before BONUS)
    if j == 21:   im = pg("1CcM5Q57", 1).crop((0, 465, 1653, 1255))                 # full-width exercise mis-read as two columns
    if j == 23:   im = im.crop((0, 22, im.width, im.height))                         # header scrap "Se préparer au devoir"
    if j == 127:  im = im.crop((0, 0, im.width, im.height - 20))
    if j == 111:  im = im.crop((0, 0, im.width, im.height - 155))                    # grading lines under the exercise
    fid = re.search(r"dv2_([\w-]{8})", e["file"]).group(1)
    yr, lab, full = INFO[fid]
    yr = re.sub(r"^(\d\d)-(\d{4})$", lambda g: "20%s-%s" % g.groups(), yr)
    yr = "" if yr == "?" else yr
    yr = re.sub(r"^(\d\d)-(\d\d)$", lambda g: "20%s-20%s" % g.groups(), yr)
    i = "D%03d" % n
    im.save(os.path.join(OUT, i + ".png"), dpi=(200, 200))
    rows.append(dict(id=i, topic=t, doc=("Devoir 2e semestre %s - %s" % (yr, lab)).replace("  ", " "), label="Ex. %d" % j,
                     link="https://drive.google.com/file/d/%s/view" % full, difficulty=d, file=i + ".png", src_index=j))
json.dump(rows, open(os.path.join(HERE, "work", "sup2_set.json"), "w"), ensure_ascii=False, indent=1)
print(len(rows), [(r["id"], r["doc"]) for r in rows][:3])
