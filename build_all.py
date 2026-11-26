#!/usr/bin/env python3
"""Two combined PDFs, same compact layout as the printed one:
  output/complet_1bacsm_seed<SEED>.pdf   : everything (printed set + supplements 1, 2, 3)
  output/nouveaux_1bacsm_seed<SEED>.pdf  : only what is NOT in the printed PDF (supplements 1, 2, 3)
IDs stay the same as in the other files (E##/M###, D###, T###). Translated exercises (arabe/*.tex)
are rendered to PNG with pdflatex first.  usage: python3 build_all.py [SEED]"""
import csv, glob, json, os, random, re, shutil, subprocess, sys
from PIL import Image
import build_pdf as B

HERE, OUT, SEED = B.HERE, B.OUT, B.SEED

# ---- printed set (203) -----------------------------------------------------------------
printed = B.EXERCISES[:]
RATE = {e[0]: B.RATE(e[0]) for e in printed}
ORIGIN = {e[0]: "PDF imprimé" for e in printed}
LANG = {e[0]: "French" for e in printed}
SRC = {e[0]: B.SOURCE(e[0]) for e in printed}

# ---- supplements 1 and 2 (typed crops) -----------------------------------------------------
new = []
for setf, imgdir, origin in (("sup_set.json", "ex_sup", "Supplément 1"), ("sup2_set.json", "ex_sup2", "Supplément 2")):
    for r in json.load(open(os.path.join(HERE, "work", setf), encoding="utf8")):
        B.DOCS.setdefault(r["doc"], (r["doc"], r["link"]))
        new.append((r["id"], r["topic"], r["doc"], r["label"], [("@png", os.path.join(HERE, "work", imgdir, r["file"]))]))
        RATE[r["id"]], ORIGIN[r["id"]], LANG[r["id"]] = r["difficulty"], origin, "French"
        SRC[r["id"]] = "mathmanti2 (mathmanti2.webnode.fr)"

# ---- supplement 3 (translated, LaTeX -> PNG) ---------------------------------------------
tex = []
for path in sorted(glob.glob(os.path.join(HERE, "arabe", "*.tex"))):
    src = open(path, encoding="utf8").read()
    h = re.search(r"%\s*source:\s*manti\.01\.ma,\s*([^(]*)\(Drive\s+([\w-]+)\)", src)
    title = "manti.01.ma - " + h.group(1).strip().rstrip(".").replace("1ère SM, ", "")
    for m in re.finditer(r"\\ex\{([^}]*)\}\{([^}]*)\}\{([^}]*)\}\{(\d+)\}(.*?)\\fin", src, re.S):
        tex.append(dict(topic=m.group(1), label=m.group(3), diff=int(m.group(4)), body=m.group(5).strip(),
                        doc="%s [%s]" % (title, m.group(2)), link="https://drive.google.com/file/d/%s/view" % h.group(2)))
TDIR = os.path.join(HERE, "work", "ex_tr"); BUILD = os.path.join(OUT, "_tex_render")
os.makedirs(TDIR, exist_ok=True); os.makedirs(BUILD, exist_ok=True)
L = [r"""\documentclass[10pt]{article}
\usepackage[T1]{fontenc}\usepackage[utf8]{inputenc}\usepackage[french]{babel}\usepackage{lmodern}
\usepackage{amsmath,amssymb}\usepackage[inline]{enumitem}
\usepackage[paperwidth=112mm,paperheight=400mm,margin=3mm]{geometry}
\setlength{\parindent}{0pt}\pagestyle{empty}\setlist{nosep,leftmargin=*,itemsep=0.8pt}\setlist[enumerate,2]{label=\alph*)}
\begin{document}"""]
for e in tex:
    L.append(r"\textbf{Exercice} \textit{(traduit de l'arabe)}\par\smallskip " + e["body"] + r"\par\newpage")
L.append(r"\end{document}")
open(os.path.join(BUILD, "t.tex"), "w", encoding="utf8").write("\n".join(L))
r = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "t.tex"], cwd=BUILD, capture_output=True, text=True, errors="replace")
if r.returncode:
    print(r.stdout[-2000:]); sys.exit(1)
for f in glob.glob(os.path.join(BUILD, "pg-*.png")): os.remove(f)
subprocess.run(["pdftoppm", "-r", "200", "-png", "t.pdf", "pg"], cwd=BUILD, check=True)
pages = sorted(glob.glob(os.path.join(BUILD, "pg-*.png")))
assert len(pages) == len(tex), (len(pages), len(tex))
for i, (e, pg) in enumerate(zip(tex, pages), 1):
    tid = "T%03d" % i
    im = Image.open(pg).convert("RGB")
    bb = im.convert("L").point(lambda v: 255 if v < 200 else 0).getbbox()
    im.crop((0, 0, im.width, min(im.height, bb[3] + 12))).save(os.path.join(TDIR, tid + ".png"), dpi=(200, 200))
    B.DOCS.setdefault(e["doc"], (e["doc"], e["link"]))
    new.append((tid, e["topic"], e["doc"], e["label"] + " (traduit de l'arabe)", [("@png", os.path.join(TDIR, tid + ".png"))]))
    RATE[tid], ORIGIN[tid], LANG[tid] = e["diff"], "Supplément 3", "French (traduit de l'arabe)"
    SRC[tid] = "manti.01.ma"

B.RTXT = lambda i: "%s/20" % RATE[i] if RATE.get(i) is not None else ""


def make(items, name, cover, csvname):
    order = items[:]
    random.Random(SEED).shuffle(order)
    pages = B.plan(order); order = B.sorted_by_print(pages)
    log = {}
    B.build(pages, log, outname=name, cover=cover)
    pdf = B.build(pages, log, outname=name, cover=cover)
    with open(os.path.join(OUT, csvname), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "topic", "language", "origin", "source", "link", "document", "exercise", "difficulty_20", "pdf_order", "pdf_page", "seed"])
        for n, ex in enumerate(order, 1):
            t, l = B.DOCS[ex[2]]
            w.writerow([ex[0], ex[1], LANG[ex[0]], ORIGIN[ex[0]], SRC[ex[0]], l, t, ex[3], RATE.get(ex[0]), n, log.get(ex[0]), SEED])
    print(pdf, len(order), "exercices")


make(printed + new, f"complet_1bacsm_seed{SEED}.pdf",
     ("Recueil complet — Entraînement 1ère Bac SM", "Tous les énoncés réunis (PDF imprimé + suppléments 1, 2, 3) · Ensembles · Applications · Fonctions · Suites"),
     "complet_exercices.csv")
make(new, f"nouveaux_1bacsm_seed{SEED}.pdf",
     ("Nouveaux énoncés — Entraînement 1ère Bac SM", "Exercices absents du PDF imprimé (suppléments 1, 2, 3) · Ensembles · Applications · Fonctions · Suites"),
     "nouveaux_exercices.csv")
