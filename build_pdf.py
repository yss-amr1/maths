#!/usr/bin/env python3
"""Build the Math Manti 1BAC SM practice PDF (énoncés only) from already-collected pages.

Usage:  python3 build_pdf.py [SEED]
  Re-run with a new SEED to reshuffle without searching again.
Inputs : PAGES dir (200-dpi PNG renders of the downloaded source PDFs) + the EXERCISES table below.
Outputs: output/math_manti_1bacsm_seed<SEED>.pdf and output/exercices.csv
Personal study use only - do not republish the source material.
"""
import csv, json, os, random, sys, datetime
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer,
                                Image as RLImage, KeepTogether, PageBreak, Table, TableStyle, Flowable)

HERE = os.path.dirname(os.path.abspath(__file__))
PAGES = os.environ.get("PAGES_DIR", os.path.join(HERE, "work", "pages"))
OUT = os.path.join(HERE, "output")
SEED = int(next((a for a in sys.argv[1:] if a.isdigit()), 20261124))

D = "https://drive.google.com/file/d/"
SITE = "https://sites.google.com/site/mathmanti/"
DOCS = {
    "CC2_2019": ("Contrôle continu 2 (S1), 1bac SM, 23/10/2019", D + "1pt82WNOyuudEyAnrXkMYzvKbPU0PYR7c/view"),
    "CC2_2019b": ("Feuille sans en-tête (même fichier que CC2 S1 23/10/2019)", D + "1pt82WNOyuudEyAnrXkMYzvKbPU0PYR7c/view"),
    "CC3_2019": ("Contrôle continu 3 (S1), 1bac SM, 29/11/2019", D + "11yKEFcS3uz65NLyTc9edukpl3mrciVF0/view"),
    "CC4_2019": ("Contrôle continu 4 (S1), 1bac SM, 13/12/2019", D + "1hmaJiTLmavfiqpibt4rai85HV-DbujUS/view"),
    "CC2_2020": ("Contrôle continu 2 (S1), 1bac SM, 30/12/2020", D + "1TUN_TWvm8Nzw8GM8_OnjzmelZIb2jfjR/view"),
    "CC2S2_2021": ("Contrôle continu 2 (S2), 1bac SM, mars 2021", D + "1NtEaXJWe3j00bx7azSmZCeMP80ylz1o2/view"),
}
# id, topic, doc, exercise label, crops [(page png, (x0,y0,x1,y1))...] (200-dpi pixel coords; several crops are stitched)
EXERCISES = [
    ("E01", "Ensembles", "CC2_2019", "Ex. 3", [("devoir2_1BACSM-1", (40, 1048, 1334, 1402))]),
    ("E02", "Ensembles", "CC2_2019", "Ex. 4", [("devoir2_1BACSM-1", (40, 1403, 1334, 1918))]),
    ("E03", "Ensembles", "CC2_2019b", "exercices (3,75 pts)", [("devoir2_1BACSM-2", (0, 40, 1425, 620))]),
    ("E04", "Ensembles", "CC3_2019", "Ex. 2", [("ctrl3_1SM-1", (40, 548, 1170, 846))]),
    ("E05", "Ensembles", "CC3_2019", "Ex. 1", [("ctrl3_1SM-1", (40, 180, 1170, 553))]),
    ("E06", "Applications", "CC3_2019", "Ex. 3", [("ctrl3_1SM-1", (40, 845, 1170, 1313))]),
    ("E07", "Applications", "CC3_2019", "Ex. 4", [("ctrl3_1SM-1", (40, 1313, 1170, 1640)), ("ctrl3_1SM-2", (20, 68, 1225, 375))]),
    ("E08", "Applications", "CC3_2019", "Ex. 5", [("ctrl3_1SM-2", (20, 385, 1225, 820))]),
    ("E09", "Applications", "CC4_2019", "Ex. 1", [("ctrl4_1SM-1", (40, 195, 1337, 1373))]),
    ("E10", "Fonctions", "CC4_2019", "Ex. 2", [("ctrl4_1SM-1", (40, 1372, 1337, 1845)), ("ctrl4_1SM-2", (30, 55, 1337, 725))]),
    ("E11", "Fonctions", "CC4_2019", "Bonus", [("ctrl4_1SM-2", (100, 745, 1337, 940))]),
    ("E12", "Ensembles", "CC2_2020", "Ex. 1", [("ctrl2_1ereBACSM-1", (55, 235, 1605, 514))]),
    ("E13", "Ensembles", "CC2_2020", "Ex. 2", [("ctrl2_1ereBACSM-1", (55, 499, 1605, 815))]),
    ("E14", "Ensembles", "CC2_2020", "Ex. 3", [("ctrl2_1ereBACSM-1", (55, 800, 1605, 1120))]),
    ("E15", "Applications", "CC2_2020", "Ex. 4", [("ctrl2_1ereBACSM-1", (55, 1105, 1605, 1540))]),
    ("E16", "Applications", "CC2_2020", "Ex. 5", [("ctrl2_1ereBACSM-1", (55, 1525, 1605, 1936))]),
    ("E17", "Ensembles", "CC2_2020", "Bonus", [("ctrl2_1ereBACSM-1", (55, 1921, 1605, 2171))]),
    ("E18", "Suites", "CC2S2_2021", "Ex. 1", [("ctrl2S2_1BACSM-1", (50, 279, 1610, 1425))]),
]
TOPICS = ["Ensembles", "Applications", "Fonctions", "Suites"]

# second source: typed series from mathmanti2.webnode.fr (already segmented into work/ex_new/*.png + work/new_set.json)
NEW = os.path.join(HERE, "work", "new_set.json")
if os.path.exists(NEW):
    for r in json.load(open(NEW, encoding="utf8")):
        key = "N:" + r["doc"]
        DOCS.setdefault(key, (r["doc"], r["link"]))
        EXERCISES.append((r["id"], r["topic"], key, r["label"], [("@png", os.path.join(HERE, "work", "ex_new", r["id"] + ".png"))]))
SOURCE = lambda ex_id: "mathmanti2 (mathmanti2.webnode.fr)" if ex_id.startswith("M") else "mathmanti (sites.google.com/site/mathmanti)"


def autotrim(im, pad=6):
    """Trim blank margins only when the background is near-white (typed sheets)."""
    g = im.convert("L")
    h = g.histogram(); half = g.width * g.height / 2; acc = 0
    for med, c in enumerate(h):
        acc += c
        if acc >= half: break
    if med < 235:
        return im
    bbox = g.point(lambda v: 255 if v < 200 else 0).getbbox()
    if not bbox:
        return im
    x0, y0, x1, y1 = bbox
    return im.crop((max(0, x0 - pad), max(0, y0 - pad), min(im.width, x1 + pad), min(im.height, y1 + pad)))


def make_crop(ex_id, crops):
    parts = []
    for page, box in crops:
        if page == "@png":
            parts.append(Image.open(box).convert("RGB")); continue
        im = Image.open(os.path.join(PAGES, page + ".png")).convert("RGB").crop(box)
        parts.append(autotrim(im))
    if len(parts) == 1:
        out = parts[0]
    else:  # exercise continues on the next page: stitch the parts, same width
        w = max(p.width for p in parts)
        out = Image.new("RGB", (w, sum(p.height for p in parts) + 8 * (len(parts) - 1)), (255, 255, 255))
        y = 0
        for p in parts:
            out.paste(p, (0, y)); y += p.height + 8
    path = os.path.join(OUT, "crops", ex_id + ".png")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    out.save(path, dpi=(200, 200))
    return path, out.size


class PageLogger(Flowable):
    """Zero-size flowable that records on which page an exercise starts."""
    def __init__(self, ex_id, log):
        super().__init__(); self.ex_id, self.log = ex_id, log
    def wrap(self, aw, ah): return (0, 0)
    def draw(self): self.log[self.ex_id] = self.canv.getPageNumber()


def build(order, pagelog, index_pages=None, outname=None, lesson=None):
    os.makedirs(OUT, exist_ok=True)
    pdf = os.path.join(OUT, outname or f"math_manti_1bacsm_seed{SEED}.pdf")
    W, H = A4
    m = 18 * mm
    cw = W - 2 * m
    doc = BaseDocTemplate(pdf, pagesize=A4, leftMargin=m, rightMargin=m, topMargin=16 * mm, bottomMargin=16 * mm,
                          title="Entraînement 1ère Bac SM%s - énoncés (Math Manti)" % (" - " + lesson if lesson else ""), author="Compilation personnelle")

    def footer(c, d):
        c.saveState(); c.setFont("Helvetica", 8); c.setFillColor(colors.grey)
        c.drawCentredString(W / 2, 9 * mm, f"Usage personnel — énoncés uniquement — page {d.page}")
        c.restoreState()
    doc.addPageTemplates([PageTemplate(id="p", frames=[Frame(m, 16 * mm, cw, H - 32 * mm, id="f", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)], onPage=footer)])

    h1 = ParagraphStyle("h1", fontName="Helvetica-Bold", fontSize=22, leading=28, alignment=TA_CENTER, spaceAfter=6)
    sub = ParagraphStyle("sub", fontName="Helvetica", fontSize=11, leading=15, alignment=TA_CENTER, textColor=colors.HexColor("#444444"))
    cap = ParagraphStyle("cap", fontName="Helvetica", fontSize=7.8, leading=10, textColor=colors.HexColor("#555555"), spaceBefore=2)
    body = ParagraphStyle("body", fontName="Helvetica", fontSize=10, leading=14)
    st = []
    # cover
    counts = {t: sum(1 for e in order if e[1] == t) for t in TOPICS}
    st += [Spacer(1, 45 * mm), Paragraph(("Leçon : " + lesson + " — " if lesson else "") + "Entraînement — 1ère Bac Sciences Mathématiques", h1),
           Paragraph("Énoncés seuls" if lesson else "Énoncés seuls · Ensembles · Applications · Fonctions · Suites", sub), Spacer(1, 12 * mm)]
    rows = [["Thème", "Exercices"]] + [[t, str(counts[t])] for t in TOPICS if counts[t]] + [["Total", str(len(order))]]
    tb = Table(rows, colWidths=[60 * mm, 30 * mm], hAlign="CENTER")
    tb.setStyle(TableStyle([("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 10), ("FONT", (0, 1), (-1, -2), "Helvetica", 10),
                            ("FONT", (0, -1), (-1, -1), "Helvetica-Bold", 10), ("LINEBELOW", (0, 0), (-1, 0), 0.8, colors.black),
                            ("LINEABOVE", (0, -1), (-1, -1), 0.8, colors.black), ("ALIGN", (1, 0), (1, -1), "CENTER"),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 5), ("TOPPADDING", (0, 0), (-1, -1), 5)]))
    st += [tb, Spacer(1, 12 * mm),
           Paragraph((f"Leçon : <b>{lesson}</b> — ordre des séries d'origine" if lesson else f"Ordre aléatoire — graine (seed) : <b>{SEED}</b>") + f" · généré le {datetime.date.today().isoformat()}", sub), Spacer(1, 4 * mm),
           Paragraph("Source : documents publics des sites « mathmanti » (Google Sites) et « mathmanti2 » (Webnode) de Bouchaib Manti. Aucune correction incluse. "
                     "Usage personnel uniquement — ne pas republier.", sub), PageBreak()]
    # exercises
    for n, ex in enumerate(order, 1):
        ex_id, topic, doc_key, label, _ = ex
        path, (pw, ph) = make_crop(ex_id, ex[4])
        natural = pw / 200 * 25.4 * mm * 1.05          # do not enlarge beyond ~105 % of the 200-dpi size
        w = min(cw, natural, (pw / ph) * 225 * mm)       # keep any block under 225 mm tall
        h = w * ph / pw
        title, link = DOCS[doc_key]
        caption = Paragraph(f"<b>{n}.</b> [{ex_id}] {topic} — Math Manti ({SOURCE(ex_id).split()[0]}) · {title} · {label}", cap)
        st.append(KeepTogether([PageLogger(ex_id, pagelog), RLImage(path, width=w, height=h), caption, Spacer(1, 9 * mm)]))
    # index at the end
    st += [PageBreak(), Paragraph("Index", ParagraphStyle("ih", fontName="Helvetica-Bold", fontSize=16, spaceAfter=8))]
    idx = [["#", "ID", "Thème", "Document", "Exercice", "Page"]]
    for n, ex in enumerate(order, 1):
        idx.append([str(n), ex[0], ex[1], DOCS[ex[2]][0], ex[3], str(pagelog.get(ex[0], "?"))])
    it = Table(idx, colWidths=[8 * mm, 12 * mm, 24 * mm, 83 * mm, 34 * mm, 12 * mm], repeatRows=1)
    it.setStyle(TableStyle([("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 8), ("FONT", (0, 1), (-1, -1), "Helvetica", 7.8),
                            ("LINEBELOW", (0, 0), (-1, 0), 0.8, colors.black), ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f3f3f3")]),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 3), ("TOPPADDING", (0, 0), (-1, -1), 3)]))
    st.append(it)
    doc.build(st)
    return pdf


def block_height_mm(ex):
    """Estimated height (mm) of an exercise block: image + 2-line caption + spacing."""
    path, (pw, ph) = make_crop(ex[0], ex[4])
    cw = A4[0] - 36 * mm
    w = min(cw, pw / 200 * 25.4 * mm * 1.05, (pw / ph) * 225 * mm)
    return w * ph / pw / mm + 21


def pack(order, avail_mm=A4[1] / mm - 32, window=8):
    """Look-ahead packing: keep the shuffled order, but when the next block does not fit on the
    current page take the first of the next `window` blocks that does (blocks never split)."""
    rem, out, left = list(order), [], avail_mm
    while rem:
        pick = next((i for i, e in enumerate(rem[:window]) if block_height_mm(e) <= left), None)
        if pick is None:
            left, pick = avail_mm, 0
        e = rem.pop(pick)
        out.append(e)
        left -= block_height_mm(e)
    return out


def by_lesson():
    """One PDF per topic, exercises in source order (series by series), no shuffle."""
    key = lambda e: (DOCS[e[2]][0].startswith('Contrôle') or DOCS[e[2]][0].startswith('Feuille'), DOCS[e[2]][0], e[0])
    for t in TOPICS:
        order = pack(sorted([e for e in EXERCISES if e[1] == t], key=key))
        log = {}
        name = f"lecon_{t.lower()}.pdf"
        build(order, log, outname=name, lesson=t)
        print(build(order, log, outname=name, lesson=t), len(order))


def main():
    order = EXERCISES[:]
    random.Random(SEED).shuffle(order)
    order = pack(order)
    log = {}
    build(order, log)          # pass 1: learn page numbers
    pdf = build(order, log)    # pass 2: index now filled (index is after the exercises, so pages do not move)
    with open(os.path.join(OUT, "exercices.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "topic", "language", "source", "link", "document", "exercise", "pdf_order", "pdf_page", "seed"])
        for n, ex in enumerate(order, 1):
            title, link = DOCS[ex[2]]
            w.writerow([ex[0], ex[1], "French", SOURCE(ex[0]) + " - public Drive file", link, title, ex[3], n, log.get(ex[0]), SEED])
    print("PDF:", pdf, "| seed", SEED, "| order:", " ".join(e[0] for e in order))


if __name__ == "__main__":
    if "--by-lesson" in sys.argv:
        by_lesson()
    else:
        main()
