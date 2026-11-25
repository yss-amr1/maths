#!/usr/bin/env python3
"""Turn the segmenter output into work/ex_new/*.png + work/new_set.json (ids M001...).
usage: gen_new_set.py WORKDIR(wn2)   (expects ex/, final_set.json, map.json, seg/)"""
import json, os, re, sys, shutil
W = sys.argv[1]; os.chdir(W)
d = json.load(open('final_set.json')); mp = json.load(open('map.json'))
DUPS = {'suites_dvs_dvs_p1c0k1', 'suites_dvs_dvs_p1c0k2', 'suites_dvs_dvs_p1c0k3', 'suites_dvs_dvs_p1c0k4'}  # same statements as suites_s4 / suites_s2
order = {x['id']: (x['rank'], x['page'], x['id']) for x in d['kept']}
for a, b in d['dups']: order.setdefault(a, (99, 0, a))
ids = sorted([i for i in order if i not in DUPS], key=lambda i: order[i])
srcmap = {(g + '_' + (n if n != '?' else 'x') + '_' + i[:6]): (g, n, i) for g, n, i in mp}
OUT = '/home/user/maths/work/ex_new'
shutil.rmtree(OUT, ignore_errors=True); os.makedirs(OUT)
ENS = ('ens_app_s1', 'ens_app_s3', 'ens_app_s4', 'ens_app_s6', 'ens_app_s10')
rows = []
for eid in ids:
    k = [k for k in srcmap if eid.startswith(k.rsplit('_', 1)[0] + '_p')][0]
    g, n, i = srcmap[k]; short = k.rsplit('_', 1)[0]
    if short.startswith('fonctions'): topic, title = 'Fonctions', f"Généralités sur les fonctions — série {n}"
    elif short.startswith('suites'):
        topic = 'Suites'
        title = ('Exercices de suites (fichier « exo »)' if short.startswith('suites_exo') else 'Exercices des suites (fichier « SC »)' if short.startswith('suites_SC') else f"Suites numériques — série {n}")
    elif short.startswith('ens_app_exo'): topic, title = 'Applications', "Exercices d'applications (fichier « exo »)"
    elif short in ENS: topic, title = 'Ensembles', f"Les ensembles — série {n}"
    else: topic, title = 'Applications', f"Les applications — série {n}"
    m = re.search(r'_p(\d+)c(\d+)k(\d+)$', eid)
    nid = f"M{len(rows)+1:03d}"
    shutil.copy(f'ex/{eid}.png', f'{OUT}/{nid}.png')
    rows.append(dict(id=nid, src_id=eid, topic=topic, doc=title, label=f"p.{m[1]} · col.{int(m[2])+1} · n°{m[3]}", link=f"https://drive.google.com/file/d/{i}/view", file=short))
json.dump(rows, open('/home/user/maths/work/new_set.json', 'w'), ensure_ascii=False, indent=1)
from collections import Counter
print(len(rows), dict(Counter(r['topic'] for r in rows)))
