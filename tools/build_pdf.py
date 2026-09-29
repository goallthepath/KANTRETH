"""Setzt Kapitel 1 von KANTRETH als Buch-PDF (A5, Garamond).

Aufruf:  python tools/build_pdf.py
Quelle:  buch/kapitel-01-der-letzte-stapellauf.md
Ziel:    buch/KANTRETH_Kapitel_01_Der_letzte_Stapellauf.pdf
"""
import re
from pathlib import Path

from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A5
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Frame, NextPageTemplate,
                                PageBreak, PageTemplate, Paragraph, Spacer)

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "buch" / "kapitel-01-der-letzte-stapellauf.md"
OUT = ROOT / "buch" / "KANTRETH_Kapitel_01_Der_letzte_Stapellauf.pdf"
REPO = "https://github.com/goallthepath/KANTRETH"

FONTS = "C:/Windows/Fonts/"
pdfmetrics.registerFont(TTFont("Gara", FONTS + "GARA.TTF"))
pdfmetrics.registerFont(TTFont("Gara-It", FONTS + "GARAIT.TTF"))
pdfmetrics.registerFont(TTFont("Gara-Bd", FONTS + "GARABD.TTF"))
pdfmetrics.registerFontFamily("Gara", normal="Gara", italic="Gara-It",
                              bold="Gara-Bd", boldItalic="Gara-Bd")

INK = "#1d1b18"
MUTED = "#6b645a"

body = ParagraphStyle("body", fontName="Gara", fontSize=11.2, leading=15.2,
                      alignment=TA_JUSTIFY, firstLineIndent=4.5 * mm,
                      textColor=INK, hyphenationLang="de_DE",
                      embeddedHyphenation=1, uriWasteReduce=0.3)
first = ParagraphStyle("first", parent=body, firstLineIndent=0)
sign = ParagraphStyle("sign", parent=body, alignment=TA_CENTER,
                      firstLineIndent=0, spaceBefore=6, spaceAfter=6)
center = ParagraphStyle("center", parent=first, alignment=TA_CENTER,
                        hyphenationLang=None)
small = ParagraphStyle("small", parent=center, fontSize=8.6, leading=12,
                       textColor=MUTED)
kicker = ParagraphStyle("kicker", parent=center, fontSize=9, leading=12,
                        textColor=MUTED)
h_title = ParagraphStyle("h_title", parent=center, fontName="Gara",
                         fontSize=34, leading=40)
h_sub = ParagraphStyle("h_sub", parent=center, fontName="Gara-It",
                       fontSize=14, leading=19)
h_chap = ParagraphStyle("h_chap", parent=center, fontName="Gara-It",
                        fontSize=19, leading=24)


def spaced(text):
    """Gesperrter Versalsatz für Titelzeilen."""
    return "&nbsp;".join(text.upper())


def inline(md):
    md = md.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    md = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", md)
    return re.sub(r"\*(.+?)\*", r"<i>\1</i>", md)


def chapter_paragraphs():
    """Nur der Romantext: zwischen Kapitelüberschrift und Schluss-Trenner."""
    lines = SRC.read_text(encoding="utf-8").splitlines()
    start = next(i for i, l in enumerate(lines) if l.startswith("Am sechsten Morgen"))
    end = max(i for i, l in enumerate(lines) if l.strip() == "---")
    paras, buf = [], []
    for line in lines[start:end]:
        if line.strip():
            buf.append(line.strip())
        elif buf:
            paras.append(" ".join(buf)); buf = []
    if buf:
        paras.append(" ".join(buf))
    return paras


def on_text_page(canvas, doc):
    canvas.saveState()
    w, h = A5
    canvas.setFont("Gara", 8.2)
    canvas.setFillColor(MUTED)
    label = "KANTRETH" if doc.page % 2 == 0 else "Der letzte Stapellauf"
    canvas.drawCentredString(w / 2, h - 13 * mm, label)
    canvas.drawCentredString(w / 2, 11 * mm, str(doc.page))
    canvas.restoreState()


def on_plain_page(canvas, doc):
    pass


def on_opening_page(canvas, doc):
    """Kapitelanfang: nur Seitenzahl, kein Kolumnentitel."""
    canvas.saveState()
    canvas.setFont("Gara", 8.2)
    canvas.setFillColor(MUTED)
    canvas.drawCentredString(A5[0] / 2, 11 * mm, str(doc.page))
    canvas.restoreState()


def build():
    w, h = A5
    doc = BaseDocTemplate(
        str(OUT), pagesize=A5, title="KANTRETH – Kapitel 1: Der letzte Stapellauf",
        author="goallthepath", subject="KANTRETH, Akt I – Salzbok: Das Schiff ohne Namen",
        keywords="KANTRETH, Roman, Leseprobe, Salzbok, Fantasy, Literatur, goallthepath",
        creator=REPO)
    frame = Frame(17 * mm, 18 * mm, w - 34 * mm, h - 38 * mm, id="f",
                  leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    doc.addPageTemplates([
        PageTemplate("plain", [frame], onPage=on_plain_page),
        PageTemplate("opening", [frame], onPage=on_opening_page),
        PageTemplate("text", [frame], onPage=on_text_page),
    ])

    s = []
    # Titelei
    s += [Spacer(1, 42 * mm), Paragraph(spaced("Kantreth"), h_title),
          Spacer(1, 7 * mm), Paragraph("Akt I — Salzbok", h_sub),
          Paragraph("Das Schiff ohne Namen", h_sub), Spacer(1, 30 * mm),
          Paragraph("Erstes Kapitel · Leseprobe", kicker), Spacer(1, 3 * mm),
          Paragraph("goallthepath", center), PageBreak()]
    s += [Spacer(1, 70 * mm),
          Paragraph("<i>Ein Schiff erhielt seinen Namen in Salzbok erst auf dem Wasser.</i>", center),
          Spacer(1, 50 * mm),
          Paragraph(f"© 2026 goallthepath. Lizenz: CC BY-NC-ND 4.0<br/>"
                    f"Weitergeben ausdrücklich erwünscht – mit Namensnennung, "
                    f"nicht kommerziell, unverändert.<br/>"
                    f'<a href="{REPO}" color="{MUTED}">github.com/goallthepath/KANTRETH</a>', small),
          NextPageTemplate("opening"), PageBreak()]
    # Kapitelkopf
    s += [Spacer(1, 22 * mm), Paragraph("Kapitel 1", kicker), Spacer(1, 3 * mm),
          Paragraph("Der letzte Stapellauf", h_chap), Spacer(1, 16 * mm),
          NextPageTemplate("text")]

    after_break = True
    for p in chapter_paragraphs():
        if p == "---":
            s.append(Paragraph("*&nbsp;&nbsp;&nbsp;*&nbsp;&nbsp;&nbsp;*", sign))
            after_break = True
            continue
        text = inline(p)
        if p.startswith("**") and p.endswith("**"):
            s.append(Paragraph(spaced(p.strip("*")), sign))
            after_break = True
            continue
        if s and after_break and p.startswith("Am sechsten Morgen"):
            words = text.split(" ", 3)
            text = f'<font size="9.6">{" ".join(words[:3]).upper()}</font> {words[3]}'
        s.append(Paragraph(text, first if after_break else body))
        after_break = False

    # Nachsatz
    s += [NextPageTemplate("plain"), PageBreak(), Spacer(1, 60 * mm),
          Paragraph("<i>Ende des ersten Kapitels.</i>", center), Spacer(1, 12 * mm),
          Paragraph("Was ist bei dir hängen geblieben?<br/>Ein Satz, ein Mensch, eine Frage?", center),
          Spacer(1, 4 * mm),
          Paragraph(f'<a href="{REPO}/issues/new?template=leserstimme.yml" color="{INK}">'
                    f"<u>Hinterlasse eine Leserstimme</u></a>", center),
          Spacer(1, 40 * mm),
          Paragraph("KANTRETH · Akt I — Salzbok · Kapitel 1<br/>"
                    "Text und Welt: goallthepath<br/>"
                    "Creative Commons BY-NC-ND 4.0 · creativecommons.org/licenses/by-nc-nd/4.0/deed.de",
                    small)]
    doc.build(s)
    print(OUT)


if __name__ == "__main__":
    build()
