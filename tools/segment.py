#!/usr/bin/env python3
"""Segment typed 'Exercice N' series PDFs into one PNG per exercise (column-aware).
usage: segment.py SRC_DIR OUT_DIR   -> OUT_DIR/*.png + OUT_DIR/manifest.json"""
import sys, os, re, json, glob, subprocess
import xml.etree.ElementTree as ET
from PIL import Image
src, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
S = 200 / 72.0
HDR = re.compile(r'^[@\W_]*(exercices?|exrcice|ex|exercise)(\d+|\(\d+\))?[:.]?$', re.I)
bad = re.compile('[\x00-\x08\x0b\x0c\x0e-\x1f]')
manifest = []
A_BY = {'ens_app_s5': 11}
for pdf in sorted(glob.glob(os.path.join(src, '*.pdf'))):
    base = os.path.basename(pdf)[:-4]
    subprocess.run(['pdftoppm', '-r', '200', '-png', pdf, os.path.join(out, '_pg_' + base)], check=True)
    x = subprocess.run(['pdftotext', '-bbox', pdf, '-'], capture_output=True, text=True, errors='replace').stdout
    x = bad.sub('', re.sub(r'<!DOCTYPE[^>]*>', '', x)).replace('xmlns="http://www.w3.org/1999/xhtml"', '')
    root = ET.fromstring(x)
    pages = list(root.iter('page'))
    last = None
    for pi, pg in enumerate(pages, 1):
        W = float(pg.get('width')); H = float(pg.get('height'))
        words = [((w.text or ''), float(w.get('xMin')), float(w.get('yMin')), float(w.get('xMax')), float(w.get('yMax'))) for w in pg.iter('word')]
        hdrs = []
        for i, (t, x0, y0, x1, y1) in enumerate(words):
            if HDR.match(t):
                # must start its line: no word ending just left of it on the same line
                if any(abs(w[2] - y0) < 8 and w[3] <= x0 + 1 and x0 - w[3] < 6 and re.search(r'\w', w[0]) for w in words if w is not words[i]):
                    continue
                nxt = [w[0] for w in words[i + 1:i + 3]]
                if t.lower().rstrip('s').rstrip(':.') == 'exercice' and t.lower().endswith('s') and not any(re.match(r'^[\(N°\d]', n) for n in nxt):
                    continue
                hdrs.append((x0, y0))
        if not hdrs:
            manifest.append(dict(file=base, page=pi, col=0, k=0, flag='NO_HEADER', parts=[])); continue
        # column gutters from the text itself: empty vertical bands >= 12pt between first and last word
        cov = [0] * (int(max(W, max(w[3] for w in words))) + 4)
        for w in words:
            for xx in range(max(0, int(w[1])), int(w[3]) + 1): cov[xx] += 1
        xs = sorted(round(h[0]) for h in hdrs)
        cl = []
        for v in xs:
            if cl and v - cl[-1][-1] < 90: cl[-1].append(v)
            else: cl.append([v])
        gut = []
        for c1, c2 in zip(cl, cl[1:]):
            xa, xb = sum(c1) / len(c1), sum(c2) / len(c2)
            lo, hi = int(xa + 30), int(xb + 6)
            vals = {xx: sum(cov[xx:xx + 8]) for xx in range(lo, max(lo + 1, hi - 8))}
            mv = min(vals.values())
            pts = sorted(xx for xx, v in vals.items() if v == mv)
            runs = []
            for p in pts:
                if runs and p - runs[-1][-1] <= 1: runs[-1].append(p)
                else: runs.append([p])
            best = max(runs, key=len)
            gut.append((best[0] + best[-1]) / 2.0 + 4)
        clusters = [0] * (len(gut) + 1)
        edges = [0.0] + gut + [W]
        img = Image.open(os.path.join(out, '_pg_%s-%d.png' % (base, pi))) if os.path.exists(os.path.join(out, '_pg_%s-%d.png' % (base, pi))) else Image.open(glob.glob(os.path.join(out, '_pg_%s-*%d.png' % (base, pi)))[0])
        for ci in range(len(clusters)):
            L, R = edges[ci], edges[ci + 1]
            col_h = sorted([h for h in hdrs if L <= h[0] < R], key=lambda h: h[1])
            if not col_h: continue
            colw = [w for w in words if L <= w[1] < R]
            first = col_h[0][1]
            A0 = A_BY.get(next((k for k in A_BY if base.startswith(k)), ''), 8)
            orphan = sorted([w for w in colw if w[2] < first - 6], key=lambda w: (w[2], w[1]))
            # drop leading title-like lines (few words near the top of the page, or site/level tags)
            lines = []
            for w in orphan:
                if lines and abs(lines[-1][0] - w[2]) < 5: lines[-1][1].append(w)
                else: lines.append([w[2], [w]])
            while lines and (lines[0][0] < 80 and len(lines[0][1]) <= 6 or any(re.search(r'manti|bac|1ère|1er|ensembles?|applications?|fonctions?|suites?|2016|2017|2018|2019', ww[0], re.I) and lines[0][0] < 90 for ww in lines[0][1])):
                lines.pop(0)
            if lines and last is not None:
                oy0 = min(w[2] for l in lines for w in l[1]) - 4
                box = (int(L * S), int(oy0 * S), int(R * S), int((first - A0) * S))
                if box[3] - box[1] > 25:
                    name = '%s__p%d_c%d_cont.png' % (base, pi, ci)
                    img.crop(box).save(os.path.join(out, name))
                    manifest[last]['parts'].append(name)
                    manifest[last]['text'] += ' ' + ' '.join(w[0] for l in lines for w in l[1])
                    manifest[last]['cont'] = True
            A = A_BY.get(next((k for k in A_BY if base.startswith(k)), ''), 8)   # decoration height above the header glyph
            hys = [h[1] for h in col_h] + [1e9]
            CUT = 16 if base.startswith('ens_app_s5') else 3
            Lb = []   # bottom of the last text line owned by each exercise
            for k in range(len(col_h)):
                own = [w for w in colw if hys[k] - 2 <= w[2] < hys[k + 1] - CUT]
                Lb.append(max(w[4] for w in own) if own else hys[k] + 15)
            for k, (hx, hy) in enumerate(col_h):
                top = hy - A
                if k > 0: top = max(top, Lb[k - 1] + 2)
                if k + 1 < len(col_h): bot = max(Lb[k] + 3, col_h[k + 1][1] - A)
                else: bot = Lb[k] + 5
                box = (int(L * S), int(max(top, 0) * S), int(R * S), int(min(bot, H) * S))
                if box[3] - box[1] < 30: continue
                name = '%s__p%d_c%d_%02d.png' % (base, pi, ci, k + 1)
                img.crop(box).save(os.path.join(out, name))
                txt = ' '.join(w[0] for w in sorted([w for w in colw if hy - 2 <= w[2] < min(bot, H)], key=lambda w: (round(w[2] / 4), w[1])))
                manifest.append(dict(file=base, page=pi, col=ci, k=k + 1, parts=[name], cont=False, flag='', text=txt))
                last = len(manifest) - 1
json.dump(manifest, open(os.path.join(out, 'manifest.json'), 'w'), indent=1)
print(len(manifest), 'entries;', sum(1 for m in manifest if m['parts']), 'exercises;', sum(1 for m in manifest if m.get('cont')), 'with continuation')
for m in manifest:
    if m['flag']: print('FLAG', m['file'], 'p', m['page'])
