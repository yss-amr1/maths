#!/usr/bin/env python3
"""SUPPLEMENT: new exercises (devoirs 1er semestre, mathmanti2) in a separate PDF + CSV, IDs D###.
The first PDF (M###/E## ids) is not modified. usage: python3 build_supplement.py [SEED]"""
import csv, json, os, random, sys
import build_pdf as B

TWO = "--two" in sys.argv
rows = json.load(open(os.path.join(B.HERE, "work", "sup2_set.json" if TWO else "sup_set.json"), encoding="utf8"))
B.DOCS.clear(); B.EXERCISES.clear()
for r in rows:
    B.DOCS[r["doc"]] = (r["doc"], r["link"])
    B.EXERCISES.append((r["id"], r["topic"], r["doc"], r["label"], [("@png", os.path.join(B.HERE, "work", "ex_sup2" if TWO else "ex_sup", r["file"]))]))
D = {r["id"]: r["difficulty"] for r in B.EXERCISES and rows}
B.RTXT = lambda i: f"{D[i]}/20"
SEED = B.SEED
order = B.EXERCISES[:]
random.Random(SEED).shuffle(order)
pages = B.plan(order); order = B.sorted_by_print(pages)
log = {}
cover = (("Supplément 2 — Entraînement 1ère Bac SM", "Nouveaux énoncés (devoirs du 2e semestre, sans limites) · Ensembles · Applications · Suites") if TWO else
         ("Supplément — Entraînement 1ère Bac SM", "Nouveaux énoncés (devoirs du 1er semestre) · Ensembles · Applications · Fonctions · Suites"))
name = f"supplement{2 if TWO else ''}_1bacsm_seed{SEED}.pdf"
B.build(pages, log, outname=name, cover=cover)
pdf = B.build(pages, log, outname=name, cover=cover)
with open(os.path.join(B.OUT, "supplement2_exercices.csv" if TWO else "supplement_exercices.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["id", "topic", "language", "source", "link", "document", "exercise", "difficulty_20", "pdf_order", "pdf_page", "seed"])
    for n, ex in enumerate(order, 1):
        t, l = B.DOCS[ex[2]]
        w.writerow([ex[0], ex[1], "French", "mathmanti2 (mathmanti2.webnode.fr) - public Drive file", l, t, ex[3], D[ex[0]], n, log.get(ex[0]), SEED])
print(pdf, len(order), "exercices,", max(log.values()), "pages (index incl.)")
