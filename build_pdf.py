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
from reportlab.platypus import (NextPageTemplate, FrameBreak, BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer,
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
RATINGS = json.load(open(os.path.join(HERE, 'work', 'ratings.json'))) if os.path.exists(os.path.join(HERE, 'work', 'ratings.json')) else {}
RATE = lambda i: RATINGS.get(i)
RTXT = lambda i: (f'{RATE(i)}/20' if RATE(i) is not None else '')

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


# ---- compact print layout -------------------------------------------------------------
PG_W, PG_H = A4
MARG_X, MARG_TOP, MARG_BOT, GAP = 10 * mm, 11 * mm, 13 * mm, 6 * mm
FRAME_H = PG_H - MARG_TOP - MARG_BOT
COL_W = (PG_W - 2 * MARG_X - GAP) / 2
WIDE_W = PG_W - 2 * MARG_X
SCANS = {"E%02d" % i for i in range(1, 12)}          # handwritten scans: kept large (they lose legibility when shrunk)
COL_SCALE, WIDE_SCALE, SCAN_MAX_W = 0.85, 0.82, 150 * mm


def layout(ex):
    """-> (class 'C' two-column | 'W' full width, width_pt, height_pt, caption_height_pt)"""
    path, (pw, ph) = make_crop(ex[0], ex[4])
    nat = pw / 200 * 25.4 * mm
    if ex[0] in SCANS:
        w, cls = min(SCAN_MAX_W, nat), "W"
    elif nat <= 134 * mm:
        w, cls = min(COL_W, nat * COL_SCALE), "C"
    else:
        w, cls = min(WIDE_W, nat * WIDE_SCALE), "W"
    w = min(w, (pw / ph) * (FRAME_H - 12 * mm))
    return cls, w, w * ph / pw, (7.5 if cls == "C" else 4.2) * mm


def block_h(ex):
    cls, w, h, c = layout(ex)
    return h + c + 2.2 * mm


def plan(order, window=16):
    """Pages as ('W'|'C', [items] or ([col1],[col2])). Keeps the given order, but looks ahead up to
    `window` blocks to fill a page; a block is never split."""
    rem, pages = list(order), []
    while rem:
        cls = layout(rem[0])[0]
        pool = [e for e in rem[:window] if layout(e)[0] == cls]
        cols = 2 if cls == "C" else 1
        taken, out = [], []
        for _ in range(cols):
            left, col = FRAME_H - 1.5 * mm, []
            progress = True
            while progress:
                progress = False
                for e in pool:
                    if e not in taken and block_h(e) <= left:
                        col.append(e); taken.append(e); left -= block_h(e); progress = True; break
            out.append(col)
        if not taken:                     # safety: item taller than a frame -> place alone
            taken = [rem[0]]; out = [[rem[0]]] + [[] for _ in range(cols - 1)]
        for e in taken: rem.remove(e)
        pages.append((cls, out))
    return pages


def build(pages, pagelog, outname=None, lesson=None, flat=None):
    os.makedirs(OUT, exist_ok=True)
    pdf = os.path.join(OUT, outname or f"math_manti_1bacsm_seed{SEED}.pdf")
    flat = flat or [e for _, cols in pages for col in cols for e in col]
    doc = BaseDocTemplate(pdf, pagesize=A4, leftMargin=MARG_X, rightMargin=MARG_X, topMargin=MARG_TOP, bottomMargin=MARG_BOT,
                          title="Entraînement 1ère Bac SM%s - énoncés (Math Manti)" % (" - " + lesson if lesson else ""), author="Compilation personnelle")

    def footer(c, d):
        c.saveState(); c.setFont("Helvetica", 9); c.setFillColor(colors.HexColor("#333333"))
        c.drawCentredString(PG_W / 2, 6 * mm, str(d.page))
        c.restoreState()
    fw = dict(leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    doc.addPageTemplates([
        PageTemplate(id="W", frames=[Frame(MARG_X, MARG_BOT, WIDE_W, FRAME_H, id="w", **fw)], onPage=footer),
        PageTemplate(id="C", frames=[Frame(MARG_X, MARG_BOT, COL_W, FRAME_H, id="c1", **fw), Frame(MARG_X + COL_W + GAP, MARG_BOT, COL_W, FRAME_H, id="c2", **fw)], onPage=footer)])

    h1 = ParagraphStyle("h1", fontName="Helvetica-Bold", fontSize=22, leading=28, alignment=TA_CENTER, spaceAfter=6)
    sub = ParagraphStyle("sub", fontName="Helvetica", fontSize=11, leading=15, alignment=TA_CENTER, textColor=colors.HexColor("#444444"))
    cap = ParagraphStyle("cap", fontName="Helvetica", fontSize=6.3, leading=7.6, textColor=colors.HexColor("#555555"), spaceBefore=1)
    st = []
    counts = {t: sum(1 for e in flat if e[1] == t) for t in TOPICS}
    st += [Spacer(1, 45 * mm), Paragraph(("Leçon : " + lesson + " — " if lesson else "") + "Entraînement — 1ère Bac Sciences Mathématiques", h1),
           Paragraph("Énoncés seuls" if lesson else "Énoncés seuls · Ensembles · Applications · Fonctions · Suites", sub), Spacer(1, 12 * mm)]
    rows = [["Thème", "Exercices"]] + [[t, str(counts[t])] for t in TOPICS if counts[t]] + [["Total", str(len(flat))]]
    tb = Table(rows, colWidths=[60 * mm, 30 * mm], hAlign="CENTER")
    tb.setStyle(TableStyle([("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 10), ("FONT", (0, 1), (-1, -2), "Helvetica", 10),
                            ("FONT", (0, -1), (-1, -1), "Helvetica-Bold", 10), ("LINEBELOW", (0, 0), (-1, 0), 0.8, colors.black),
                            ("LINEABOVE", (0, -1), (-1, -1), 0.8, colors.black), ("ALIGN", (1, 0), (1, -1), "CENTER"),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 5), ("TOPPADDING", (0, 0), (-1, -1), 5)]))
    st += [tb]
    n = 0
    for cls, cols in pages:
        st += [NextPageTemplate(cls), PageBreak()]
        for ci, col in enumerate(cols):
            if ci: st.append(FrameBreak())
            for ex in col:
                n += 1
                c, w, h, _ = layout(ex)
                title = DOCS[ex[2]][0]
                short = f"<b>{n}.</b> [{ex[0]}] {ex[1]} · {title} · {ex[3]} &nbsp;—&nbsp; <b>Difficulté : {RTXT(ex[0])}</b>"
                st.append(KeepTogether([PageLogger(ex[0], pagelog), RLImage(make_crop(ex[0], ex[4])[0], width=w, height=h), Paragraph(short, cap), Spacer(1, 1.6 * mm)]))
    st += [NextPageTemplate("W"), PageBreak(), Paragraph("Index", ParagraphStyle("ih", fontName="Helvetica-Bold", fontSize=14, spaceAfter=6))]
    idx = [["#", "ID", "Thème", "Document", "Exercice", "Diff.", "Page"]]
    for i, ex in enumerate(sorted_by_print(pages), 1):
        idx.append([str(i), ex[0], ex[1], DOCS[ex[2]][0], ex[3], RTXT(ex[0]), str(pagelog.get(ex[0], "?"))])
    it = Table(idx, colWidths=[8 * mm, 12 * mm, 23 * mm, 84 * mm, 34 * mm, 12 * mm, 10 * mm], repeatRows=1)
    it.setStyle(TableStyle([("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 7), ("FONT", (0, 1), (-1, -1), "Helvetica", 6.8),
                            ("LINEBELOW", (0, 0), (-1, 0), 0.6, colors.black), ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f3f3f3")]),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 1.4), ("TOPPADDING", (0, 0), (-1, -1), 1.4)]))
    st.append(it)
    doc.build(st)
    return pdf


def sorted_by_print(pages):
    return [e for _, cols in pages for col in cols for e in col]


def by_lesson():
    """One PDF per topic, exercises in source order (series by series), no shuffle."""
    key = lambda e: (DOCS[e[2]][0].startswith('Contrôle') or DOCS[e[2]][0].startswith('Feuille'), DOCS[e[2]][0], e[0])
    for t in TOPICS:
        pages = plan(sorted([e for e in EXERCISES if e[1] == t], key=key))
        log = {}
        name = f"lecon_{t.lower()}.pdf"
        build(pages, log, outname=name, lesson=t)
        print(build(pages, log, outname=name, lesson=t), len(sorted_by_print(pages)))


def main():
    order = EXERCISES[:]
    random.Random(SEED).shuffle(order)
    pages = plan(order); order = sorted_by_print(pages)
    log = {}
    build(pages, log)          # pass 1: learn page numbers
    pdf = build(pages, log)    # pass 2: index now filled (index is after the exercises, so pages do not move)
    with open(os.path.join(OUT, "exercices.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "topic", "language", "source", "link", "document", "exercise", "difficulty_20", "pdf_order", "pdf_page", "seed"])
        for n, ex in enumerate(order, 1):
            title, link = DOCS[ex[2]]
            w.writerow([ex[0], ex[1], "French", SOURCE(ex[0]) + " - public Drive file", link, title, ex[3], RATE(ex[0]), n, log.get(ex[0]), SEED])
    print("PDF:", pdf, "| seed", SEED, "| order:", " ".join(e[0] for e in order))


if __name__ == "__main__":
    if "--by-lesson" in sys.argv:
        by_lesson()
    else:
        main()
