#!/usr/bin/env python3
"""Manual crops for pages the automatic segmenter cannot split (run after gen_new_set.py).
usage: fixups.py WORKDIR(wn2)"""
import sys, os, json, glob
from PIL import Image
os.chdir(sys.argv[1])
rows = json.load(open('/home/user/maths/work/new_set.json', encoding='utf8'))
def page(name): return Image.open(glob.glob('seg/_pg_%s-*%s.png' % name)[0]).convert('RGB')
pg = glob.glob('seg/_pg_suites_s6_11ZqGM-*1.png')[0]
im = Image.open(pg).convert('RGB')
S = 200 / 72.0
def crop(y0, y1, x0=30, x1=565): return im.crop((int(x0 * S), int(y0 * S), int(x1 * S), int(y1 * S)))
S9a, S9b = page(('ens_app_s9_19_a8X', '1')), page(('ens_app_s9_19_a8X', '2'))
def cp(img, y0, y1, x0=24, x1=585): return img.crop((int(x0 * S), int(y0 * S), int(x1 * S), int(y1 * S)))
fix = {'ens_app_s9_19_p1c0k1': cp(S9a, 50, 398), 'ens_app_s9_19_p1c0k2': cp(S9a, 401, 812), 'ens_app_s9_19_p2c0k1': cp(S9b, 50, 238), 'ens_app_s9_19_p2c0k2': cp(S9b, 240, 712),
       'suites_s6_p1c0k1': crop(28, 449, 22, 585), 'suites_s6_p1c1k1': crop(450, 772, 22, 585)}
for r in rows:
    if r['src_id'] in fix:
        fix[r['src_id']].save(f"/home/user/maths/work/ex_new/{r['id']}.png"); print('fixed', r['id'], r['src_id'])
# trim the sliver of the next exercise's title under M161
for r in rows:
    if r['id'] == 'M161':
        p = f"/home/user/maths/work/ex_new/{r['id']}.png"; t = Image.open(p); t.crop((0, 0, t.width, t.height - 28)).save(p); print('trimmed', r['id'])
