#!/usr/bin/env python3
"""SUPPLEMENT 3 : exercices traduits de l'arabe (manti.01.ma, 1ère Bac SM), typeset with pdflatex.
Sources: arabe/*.tex (one file per Arabic sheet; \\ex{Thème}{code}{Ex. k}{diff} ... \\fin).
usage: python3 build_arabe.py [SEED]  -> output/supplement3_traduits_seed<SEED>.pdf + output/supplement3_exercices.csv
Ids T001..: stable, assigned in source order (file name, then position) and independent of the seed."""
import csv, glob, os, random, re, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = int(next((a for a in sys.argv[1:] if a.isdigit()), 20261124))
TOPICS = ["Ensembles", "Applications", "Fonctions", "Suites"]
OUT = os.path.join(HERE, "output")
BUILD = os.path.join(OUT, "_tex_arabe")

ex = []
for path in sorted(glob.glob(os.path.join(HERE, "arabe", "*.tex"))):
    src = open(path, encoding="utf8").read()
    head = re.search(r"%\s*source:\s*manti\.01\.ma,\s*([^(]*)\(Drive\s+([\w-]+)\)", src)
    title = "manti.01.ma - " + head.group(1).strip().rstrip(".").replace("1ère SM, ", "")
    link = "https://drive.google.com/file/d/%s/view" % head.group(2)
    for m in re.finditer(r"\\ex\{([^}]*)\}\{([^}]*)\}\{([^}]*)\}\{(\d+)\}(.*?)\\fin", src, re.S):
        ex.append(dict(topic=m.group(1), code=m.group(2), label=m.group(3), diff=int(m.group(4)),
                       body=m.group(5).strip(), doc="%s [%s]" % (title, m.group(2)), link=link))
for i, e in enumerate(ex, 1):
    e["id"] = "T%03d" % i
assert all(e["topic"] in TOPICS for e in ex)

order = ex[:]
random.Random(SEED).shuffle(order)

esc = lambda s: s.replace("&", "\\&").replace("_", "\\_").replace("#", "\\#").replace("%", "\\%")
counts = {t: sum(1 for e in ex if e["topic"] == t) for t in TOPICS}
L = [r"""\documentclass[10pt,a4paper]{article}
\usepackage[T1]{fontenc}\usepackage[utf8]{inputenc}\usepackage[french]{babel}
\usepackage{lmodern}\usepackage{amsmath,amssymb}\usepackage{multicol}\usepackage[inline]{enumitem}
\usepackage[a4paper,margin=10mm,bottom=14mm,footskip=7mm]{geometry}\usepackage{longtable,booktabs}
\setlength{\columnsep}{6mm}\setlength{\parindent}{0pt}\setlength{\columnseprule}{0.2pt}
\setlist{nosep,leftmargin=*,itemsep=0.6pt}\setlist[enumerate,2]{label=\alph*)}
\pagestyle{plain}\renewcommand{\arraystretch}{1.08}
\newcommand{\exo}[3]{\par\noindent\begin{minipage}{\columnwidth}\small\label{ex:#1}#3\par\vspace{0.6mm}
{\fontsize{6.3}{7.4}\selectfont\color[gray]{0.33}#2\par}\end{minipage}\par\vspace{2.6mm}\goodbreak}
\usepackage{xcolor}
\begin{document}
\thispagestyle{plain}\vspace*{40mm}
\begin{center}{\LARGE\bfseries Supplément 3 --- Entraînement 1ère Bac SM\par}\vspace{3mm}
{\large Énoncés traduits de l'arabe (manti.01.ma) $\cdot$ Ensembles $\cdot$ Applications $\cdot$ Fonctions $\cdot$ Suites\par}\vspace{12mm}
\begin{tabular}{lc}\toprule\textbf{Thème}&\textbf{Exercices}\\\midrule"""]
for t in TOPICS:
    L.append(r"%s&%d\\" % (t, counts[t]))
L.append(r"\midrule\textbf{Total}&\textbf{%d}\\\bottomrule\end{tabular}\end{center}" % len(ex))
L.append(r"\newpage\begin{multicols*}{2}\raggedcolumns")
for n, e in enumerate(order, 1):
    cap = r"\textbf{%d.} [%s] %s $\cdot$ %s $\cdot$ %s --- Traduit de l'arabe --- \textbf{Difficulté : %d/20}" % (
        n, e["id"], e["topic"], esc(e["doc"]), e["label"], e["diff"])
    L.append(r"\exo{%s}{%s}{\textbf{%d.}\ %s}" % (e["id"], cap, n, e["body"]))
L.append(r"\end{multicols*}\newpage{\large\bfseries Index\par}\vspace{2mm}\scriptsize")
L.append(r"\begin{longtable}{rllp{78mm}lrr}\toprule\#&ID&Thème&Document&Exercice&Diff.&Page\\\midrule\endhead")
for n, e in enumerate(order, 1):
    L.append(r"%d&%s&%s&%s&%s&%d/20&\pageref{ex:%s}\\" % (n, e["id"], e["topic"], esc(e["doc"]), e["label"], e["diff"], e["id"]))
L.append(r"\bottomrule\end{longtable}\end{document}")

os.makedirs(BUILD, exist_ok=True)
open(os.path.join(BUILD, "main.tex"), "w", encoding="utf8").write("\n".join(L))
for _ in range(2):
    r = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"], cwd=BUILD, capture_output=True, text=True, errors="replace")
    if r.returncode:
        print(r.stdout[-3000:]); sys.exit(1)
pdf = os.path.join(OUT, "supplement3_traduits_seed%d.pdf" % SEED)
shutil.copy(os.path.join(BUILD, "main.pdf"), pdf)

aux = open(os.path.join(BUILD, "main.aux"), encoding="utf8").read()
page = {m.group(1): int(m.group(2)) for m in re.finditer(r"\\newlabel\{ex:(T\d+)\}\{\{[^}]*\}\{(\d+)\}", aux)}
with open(os.path.join(OUT, "supplement3_exercices.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["id", "topic", "language", "source", "link", "document", "exercise", "difficulty_20", "pdf_order", "pdf_page", "seed"])
    for n, e in enumerate(order, 1):
        w.writerow([e["id"], e["topic"], "French (traduit de l'arabe)", "manti.01.ma - public Drive file", e["link"], e["doc"], e["label"], e["diff"], n, page.get(e["id"]), SEED])
print(pdf, len(ex), "exercices", counts, "pages:", max(page.values()))
