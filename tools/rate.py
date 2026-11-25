#!/usr/bin/env python3
"""Estimated difficulty /20 per exercise = heuristic score from the statement text, then manual overrides (ratings_manual.json).
usage: rate.py  -> work/ratings.json"""
import json, re, os
HERE = '/home/user/maths'
S = '/tmp/claude-0/-home-user-maths/a7a9c8ca-dcbf-5b0c-a069-1f957a2ad859/scratchpad/wn2/'
m = json.load(open(S + 'seg/manifest.json'))
tx = {f"{e['file'].rsplit('_',1)[0]}_p{e['page']}c{e['col']}k{e['k']}": e['text'] for e in m if e['parts']}
rows = json.load(open(f'{HERE}/work/new_set.json', encoding='utf8'))
KW = [(r'récurrence', 2.5), (r'bijecti|r[ée]ciproque', 2), (r'restriction', 1), (r'surjecti', 1), (r'injecti', 0.8), (r'g[ée]om[ée]trique', 1),
      (r'arithm[ée]tique', 0.5), (r'major|minor|born', 0.8), (r'minimum|maximum|extremum', 1), (r'∘|[fg] ?o ?[fg]', 1.2), (r'P ?\( ?E|P ?\( ?A', 1.5),
      (r'∆|Δ', 1.5), (r'∑|Σ|S ?n ?=|somme', 1.2), (r'∏', 1.5), (r'sin|cos', 1), (r'E ?\(', 1.2), (r'monotonie|croissant|d[ée]croissant', 0.6),
      (r'équivalence|⇔', 1), (r'impair|pair', 0.5), (r'équation', 0.4), (r'en extension', -1.5), (r'compr[ée]hension', 0.3), (r'paramètre|\bm\b ', 1),
      (r'proposé par', 0.0), (r'√|racine', 0.5), (r'U ?n\+? ?1|u ?n ?\+ ?1', 0.8)]
def feat(t):
    n = len(re.findall(r'(?:^|\s)(?:\d|[a-eα])\s?[\)\.]\s', t))
    return max(n, 1), len(t)
out = {}
for x in rows:
    t = tx.get(x['src_id'], '')
    n, L = feat(t)
    sc = 3.0 + 0.75 * min(n, 10) + min(L, 900) / 170.0
    for pat, w in KW:
        if re.search(pat, t, re.I): sc += w
    out[x['id']] = round(min(max(sc, 2), 19))
manual = {}
p = f'{HERE}/tools/ratings_manual.json'
if os.path.exists(p): manual = json.load(open(p))
out.update({k: v for k, v in manual.items() if not k.startswith('_')})
# handwritten / typed contrôles E01..E18 (judged from the statements)
E = dict(E01=7, E02=9, E03=11, E04=10, E05=12, E06=10, E07=13, E08=13, E09=13, E10=12, E11=15, E12=6, E13=9, E14=10, E15=12, E16=14, E17=16, E18=12)
out.update(E)
out.update({k: v for k, v in manual.items() if not k.startswith('_')})
json.dump(out, open(f'{HERE}/work/ratings.json', 'w'), indent=0)
from collections import Counter
print(len(out), sorted(Counter(out.values()).items()))
