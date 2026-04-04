from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import ListFlowable, ListItem, Paragraph, SimpleDocTemplate, Spacer


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "docs" / "project_report.md"
OUTPUT = ROOT / "docs" / "project_report.pdf"


def parse_markdown(lines):
    blocks = []
    paragraph = []
    bullets = []

    def flush_paragraph():
        nonlocal paragraph
        if paragraph:
            blocks.append(("paragraph", " ".join(paragraph).strip()))
            paragraph = []

    def flush_bullets():
        nonlocal bullets
        if bullets:
            blocks.append(("bullets", bullets[:]))
            bullets = []

    for raw_line in lines:
        line = raw_line.rstrip()
        stripped = line.strip()

        if not stripped:
            flush_paragraph()
            flush_bullets()
            continue

        if stripped.startswith("```"):
            continue

        if stripped.startswith("# "):
            flush_paragraph()
            flush_bullets()
            blocks.append(("title", stripped[2:].strip()))
            continue

        if stripped.startswith("## "):
            flush_paragraph()
            flush_bullets()
            blocks.append(("heading", stripped[3:].strip()))
            continue

        if stripped.startswith("### "):
            flush_paragraph()
            flush_bullets()
            blocks.append(("subheading", stripped[4:].strip()))
            continue

        if stripped.startswith("- "):
            flush_paragraph()
            bullets.append(stripped[2:].strip())
            continue

        if stripped[0].isdigit() and ". " in stripped:
            flush_paragraph()
            bullets.append(stripped.split(". ", 1)[1].strip())
            continue

        flush_bullets()
        paragraph.append(stripped)

    flush_paragraph()
    flush_bullets()
    return blocks


def build_pdf():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="BodyJustify",
            parent=styles["BodyText"],
            alignment=TA_JUSTIFY,
            fontName="Helvetica",
            fontSize=10.5,
            leading=15,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="DocTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=28,
            textColor=colors.HexColor("#0d7a64"),
            spaceAfter=18,
        )
    )
    styles.add(
        ParagraphStyle(
            name="HeadingCustom",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=15,
            leading=20,
            textColor=colors.HexColor("#1d2a24"),
            spaceBefore=10,
            spaceAfter=10,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SubheadingCustom",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=16,
            textColor=colors.HexColor("#9b4d1f"),
            spaceBefore=8,
            spaceAfter=6,
        )
    )

    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        rightMargin=0.65 * inch,
        leftMargin=0.65 * inch,
        topMargin=0.7 * inch,
        bottomMargin=0.7 * inch,
        title="Course Matcher Project Report",
        author="Codex",
    )

    story = []
    blocks = parse_markdown(SOURCE.read_text(encoding="utf-8").splitlines())

    for kind, content in blocks:
        if kind == "title":
            story.append(Paragraph(content, styles["DocTitle"]))
        elif kind == "heading":
            story.append(Paragraph(content, styles["HeadingCustom"]))
        elif kind == "subheading":
            story.append(Paragraph(content, styles["SubheadingCustom"]))
        elif kind == "paragraph":
            safe = (
                content.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
            )
            story.append(Paragraph(safe, styles["BodyJustify"]))
        elif kind == "bullets":
            items = []
            for item in content:
                safe = (
                    item.replace("&", "&amp;")
                    .replace("<", "&lt;")
                    .replace(">", "&gt;")
                )
                items.append(ListItem(Paragraph(safe, styles["BodyJustify"])))
            story.append(
                ListFlowable(
                    items,
                    bulletType="bullet",
                    bulletFontName="Helvetica",
                    bulletFontSize=9,
                    leftIndent=16,
                )
            )
            story.append(Spacer(1, 6))

    doc.build(story)


if __name__ == "__main__":
    build_pdf()
