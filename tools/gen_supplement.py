#!/usr/bin/env python3
"""Builds the SUPPLEMENT set (devoirs of mathmanti2.webnode.fr, 1er semestre) from segmenter output.

usage: gen_supplement.py SCRATCH   (SCRATCH holds dv/ (downloaded PDFs), dvseg2/ (segment.py output on widened PDFs), sel.json)
writes work/ex_sup/D###.png and work/sup_set.json. Nothing of the first (printed) PDF is touched.
"""
import json, os, re, sys, glob
from PIL import Image

S = sys.argv[1]
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "work", "ex_sup"); os.makedirs(OUT, exist_ok=True)
man = json.load(open(S + "/dvseg2/manifest.json"))
sel = json.load(open(S + "/sel.json"))
LINK = {x["id"][:6]: "https://drive.google.com/file/d/%s/view" % x["id"] for x in sel}

# index in manifest -> (topic, difficulty /20)
E, A, F, SU = "Ensembles", "Applications", "Fonctions", "Suites"
PICK = {
    9: (E, 8), 16: (E, 7), 76: (E, 11), 94: (E, 8), 110: (E, 8), 126: (E, 8), 142: (E, 10), 151: (E, 7), 152: (E, 8),
    17: (A, 11), 81: (A, 11), 95: (A, 11), 96: (A, 9), 106: (A, 12), 120: (A, 11), 127: (A, 11), 137: (A, 11), 153: (A, 9), 154: (A, 11),
    3: (SU, 7), 5: (SU, 8), 7: (SU, 9), 18: (SU, 12), 35: (SU, 6), 46: (SU, 12), 47: (SU, 11), 71: (SU, 9), 72: (SU, 13), 103: (SU, 11),
    111: (SU, 9), 112: (SU, 12), 128: (SU, 10), 135: (SU, 11), 136: (SU, 10), 146: (SU, 11), 74: (F, 12),
    11: (F, 10), 25: (F, 10), 26: (F, 13), 49: (F, 9), 50: (F, 12), 66: (F, 10), 67: (F, 11), 73: (F, 9), 78: (F, 12),
    82: (F, 8), 83: (F, 13), 89: (F, 13), 121: (F, 11), 129: (F, 12), 133: (F, 6), 134: (F, 11), 140: (F, 8), 141: (F, 12), 145: (F, 9), 150: (F, 8),
    155: (F, 6), 157: (F, 13), 158: (F, 9),
}


def stack(ims):
    w = max(i.width for i in ims)
    o = Image.new("RGB", (w, sum(i.height for i in ims)), "white"); y = 0
    for i in ims:
        o.paste(i, (0, y)); y += i.height
    return o


def part(e, k):
    return Image.open(S + "/dvseg2/" + e["parts"][k]).convert("RGB")


def page(prefix, n):
    return Image.open(glob.glob("%s/dvseg2/_pg_%s*-%d.png" % (S, prefix, n))[0]).convert("RGB")


def fname(prefix):
    return os.path.basename(glob.glob("%s/dv/%s*.pdf" % (S, prefix))[0])[:-4]


items = []   # (source file stem, label, image, topic, diff)
for j, (t, d) in sorted(PICK.items()):
    e = man[j]
    if j == 82:                                    # 2nd part is only the next page's header band
        im = part(e, 0)
    elif j == 89:                                  # drop the school header band at the top of the 2nd part
        im = stack([part(e, 0), part(e, 1).crop((0, 150, 1652, part(e, 1).height))])
    elif j == 74:                                  # continuation of this exercise is at the top of page 2
        im = stack([part(e, 0), page("dv_21", 2).crop((0, 150, 1653, 1100))])
    elif j == 110:                                 # its header line ended up at the bottom of the previous crop
        prev = part(man[109], 0)
        im = stack([prev.crop((0, prev.height - 76, prev.width, prev.height)), part(e, 0)])
    elif j == 47:
        im = part(e, 0); im = im.crop((0, 0, im.width, 700))
    elif j == 76:                                  # two-column page: left column only (Exercice 1); Exercice 2 is a MANUAL crop
        im = page("dv_22", 1).crop((68, 222, 728, 669))
    elif j in (83, 106, 134):                      # drop the separate BONUS exercise printed under it
        im = part(e, 0); im = im.crop((0, 0, im.width, {83: 1290, 106: 795, 134: 470}[j]))
    elif j == 81:
        im = part(e, 0); im = im.crop((0, 30, im.width, im.height - 14))
    elif j == 150:
        im = part(e, 0); im = im.crop((0, 22, im.width, im.height))
    elif j == 137:                                 # continuation (question 4b) is at the top of page 2
        im = stack([part(e, 0), page("dv_38", 2).crop((0, 225, 1654, 412))])
    elif j == 76:
        im = part(e, 0); im = im.crop((0, 0, im.width, im.height - 11))
    else:
        im = stack([part(e, k) for k in range(len(e["parts"]))])
    items.append((e["file"], j, im, t, d))

# pages the segmenter could not split: manual crops (x0,y0,x1,y1 in 1653x2339 page pixels)
MANUAL = [
    ("dv_09", 1, (0, 184, 1653, 446), E, 7, "Ex. 1"),
    ("dv_09", 1, (0, 462, 1653, 1266), SU, 11, "Ex. 2"),
    ("dv_09", 1, (0, 1290, 1653, 2050), A, 11, "Ex. 3"),
    ("dv_36", 1, (87, 285, 1561, 1575), F, 12, "Ex. 1"),
    ("dv_36", 1, (87, 1558, 764, 1970), E, 8, "Ex. 2"),
    ("dv_36", 1, (770, 1558, 1561, 2250), E, 8, "Ex. 3"),
]
for pre, pg, box, t, d, lab in MANUAL:
    items.append((fname(pre), lab, page(pre, pg).crop(box), t, d))
# dv_22 Exercice 2: its start is under Exercice 1 (left column), its questions in the right column
p22 = page("dv_22", 1)
items.append((fname("dv_22"), "Ex. 2", stack([p22.crop((68, 670, 728, 815)), p22.crop((735, 225, 1590, 715))]), E, 9))

rows = []
for n, (stem, lab, im, t, d) in enumerate(items, 1):
    i = "D%03d" % n
    im.save(os.path.join(OUT, i + ".png"), dpi=(200, 200))
    m = re.match(r"dv_\d+_(\d)_([^_]+)_(.+)_([\w-]{6})$", stem)
    sem, yr, name, fid = m.groups()
    yr = {"avant2011": "avant 2011"}.get(yr, re.sub(r"^(\d\d)-(\d{4})$", lambda g: "20%s-%s" % (g.group(1), g.group(2)), yr))
    name = name.replace("nbsp", "")
    doc = "Devoir 1er semestre %s - %s" % (yr, name)
    rows.append(dict(id=i, topic=t, doc=doc, label=("Ex. %s" % lab if isinstance(lab, int) else lab), link=LINK[fid], difficulty=d, file=i + ".png"))
json.dump(rows, open(os.path.join(HERE, "work", "sup_set.json"), "w"), ensure_ascii=False, indent=1)
print(len(rows), "exercices;", {t: sum(1 for r in rows if r["topic"] == t) for t in (E, A, F, SU)})
