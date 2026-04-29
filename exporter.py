import re
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from fpdf import FPDF


# ═══════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════

def _clean(text):
    """Strip markdown symbols."""
    return re.sub(r'[*_`#]', '', text).strip()


def _extract_abstract(content):
    """Pull abstract text from generated paper."""
    lines  = content.split('\n')
    in_abs = False
    buf    = []
    for line in lines:
        s = line.strip()
        if re.search(r'abstract', s, re.IGNORECASE) and s.startswith('#'):
            in_abs = True
            continue
        if in_abs:
            if s.startswith('#') or re.match(r'^[IVX]+\.', s):
                break
            if s:
                buf.append(_clean(s))
    return ' '.join(buf)


def _add_rule(doc):
    """Add a horizontal divider line."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after  = Pt(2)
    pPr  = p._p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    bot  = OxmlElement('w:bottom')
    bot.set(qn('w:val'),   'single')
    bot.set(qn('w:sz'),    '6')
    bot.set(qn('w:space'), '1')
    bot.set(qn('w:color'), '000000')
    pBdr.append(bot)
    pPr.append(pBdr)
    return p


def _set_two_columns(section):
    """Make a docx section use 2 equal columns."""
    sectPr = section._sectPr
    existing = sectPr.find(qn('w:cols'))
    if existing is not None:
        sectPr.remove(existing)
    cols = OxmlElement('w:cols')
    cols.set(qn('w:num'),        '2')
    cols.set(qn('w:space'),      '720')   # 0.5 inch gap
    cols.set(qn('w:equalWidth'), '1')
    sectPr.append(cols)


def _add_page_number(footer_paragraph):
    """Insert PAGE field into a paragraph."""
    run = footer_paragraph.add_run()
    run.font.size = Pt(8)
    fldChar1 = OxmlElement('w:fldChar')
    fldChar1.set(qn('w:fldCharType'), 'begin')
    instrText = OxmlElement('w:instrText')
    instrText.text = 'PAGE'
    fldChar2 = OxmlElement('w:fldChar')
    fldChar2.set(qn('w:fldCharType'), 'end')
    run._r.append(fldChar1)
    run._r.append(instrText)
    run._r.append(fldChar2)


# ═══════════════════════════════════════════════════════════
#  IEEE DOCX EXPORT  — pure Python, no Node.js
# ═══════════════════════════════════════════════════════════

ROMAN = ['I','II','III','IV','V','VI','VII','VIII','IX','X']


def save_ieee_docx(topic, content, authors="Research Agent"):
    """
    Generate an IEEE-formatted .docx:
      - Single-column title + abstract
      - Two-column body
      - Times New Roman throughout
      - Roman-numeral section headings
      - Code blocks in Courier New
    """
    filename = topic.replace(" ", "_") + "_IEEE_paper.docx"
    doc      = Document()

    # ── Page geometry (8.5 × 11 in, 0.65 in margins) ──────
    sec0 = doc.sections[0]
    sec0.page_width    = Inches(8.5)
    sec0.page_height   = Inches(11)
    sec0.left_margin   = Inches(0.65)
    sec0.right_margin  = Inches(0.65)
    sec0.top_margin    = Inches(0.75)
    sec0.bottom_margin = Inches(0.75)

    # ── Header ────────────────────────────────────────────
    hp = sec0.header.paragraphs[0]
    hp.text      = "IEEE Open Journal — Auto-Generated Research Paper"
    hp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    hp.runs[0].font.name    = 'Times New Roman'
    hp.runs[0].font.size    = Pt(8)
    hp.runs[0].font.italic  = True
    hp.runs[0].font.color.rgb = RGBColor(0x77, 0x77, 0x77)

    # ── Footer ────────────────────────────────────────────
    fp = sec0.footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _add_page_number(fp)

    # ── Title ─────────────────────────────────────────────
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run(topic)
    r.font.name = 'Times New Roman'
    r.font.size = Pt(18)
    r.font.bold = True

    # ── Authors ───────────────────────────────────────────
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run(authors)
    r.font.name   = 'Times New Roman'
    r.font.size   = Pt(10)
    r.font.italic = True

    _add_rule(doc)

    # ── Abstract heading ──────────────────────────────────
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after  = Pt(4)
    r = p.add_run("Abstract")
    r.font.name   = 'Times New Roman'
    r.font.size   = Pt(10)
    r.font.bold   = True
    r.font.italic = True

    # ── Abstract body ─────────────────────────────────────
    abstract = _extract_abstract(content) or f"This paper presents a study on {topic}."
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.left_indent  = Inches(0.4)
    p.paragraph_format.right_indent = Inches(0.4)
    p.paragraph_format.space_after  = Pt(8)
    r = p.add_run(abstract)
    r.font.name = 'Times New Roman'
    r.font.size = Pt(9)

    _add_rule(doc)

    # ── New section: 2-column body ────────────────────────
    body_sec = doc.add_section(WD_SECTION.CONTINUOUS)
    body_sec.page_width    = Inches(8.5)
    body_sec.page_height   = Inches(11)
    body_sec.left_margin   = Inches(0.65)
    body_sec.right_margin  = Inches(0.65)
    body_sec.top_margin    = Inches(0.75)
    body_sec.bottom_margin = Inches(0.75)
    _set_two_columns(body_sec)

    # ── Render body content ───────────────────────────────
    sec_idx  = 0
    in_code  = False
    code_buf = []

    def _body_text(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_after        = Pt(3)
        p.paragraph_format.first_line_indent  = Inches(0.15)
        r = p.add_run(_clean(text))
        r.font.name = 'Times New Roman'
        r.font.size = Pt(10)

    def _section_head(text):
        nonlocal sec_idx
        label = ROMAN[sec_idx] if sec_idx < len(ROMAN) else str(sec_idx + 1)
        sec_idx += 1
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after  = Pt(3)
        r = p.add_run(f"{label}. {_clean(text).upper()}")
        r.font.name = 'Times New Roman'
        r.font.size = Pt(10)
        r.font.bold = True

    def _subsection_head(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after  = Pt(2)
        r = p.add_run(_clean(text))
        r.font.name   = 'Times New Roman'
        r.font.size   = Pt(10)
        r.font.bold   = True
        r.font.italic = True

    def _code_block(lines):
        for cl in lines:
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.2)
            p.paragraph_format.space_after = Pt(0)
            pPr = p._p.get_or_add_pPr()
            shd = OxmlElement('w:shd')
            shd.set(qn('w:val'),   'clear')
            shd.set(qn('w:fill'),  'F0F0F0')
            pPr.append(shd)
            r = p.add_run(cl.replace('\t', '    '))
            r.font.name = 'Courier New'
            r.font.size = Pt(8)
        doc.add_paragraph()

    for line in content.split('\n'):
        stripped = line.strip()

        # Code block toggle
        if stripped.startswith('```'):
            if not in_code:
                in_code  = True
                code_buf = []
            else:
                in_code = False
                _code_block(code_buf)
            continue

        if in_code:
            code_buf.append(line)
            continue

        if not stripped:
            continue

        # Skip abstract (already rendered)
        if re.search(r'^#{1,3}\s*abstract', stripped, re.IGNORECASE):
            continue
        if stripped.lower() in ('see above.', 'see above'):
            continue

        # Section heading
        if re.match(r'^#{1,3}\s', stripped) or re.match(r'^[IVX]+\.\s', stripped):
            title = re.sub(r'^#{1,3}\s', '', stripped)
            title = re.sub(r'^[IVX]+\.\s', '', title)
            _section_head(title)

        # Subsection (A. B. C.)
        elif re.match(r'^[A-Z]\.\s', stripped):
            _subsection_head(stripped)

        else:
            _body_text(stripped)

    doc.save(filename)
    print(f"📄 IEEE DOCX saved: {filename}")
    return filename


# ═══════════════════════════════════════════════════════════
#  PDF EXPORT  — Unicode-safe
# ═══════════════════════════════════════════════════════════

class UnicodePDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_font("DejaVu",  "",  "DejaVuSans.ttf",         uni=True)
        self.add_font("DejaVu",  "B", "DejaVuSans-Bold.ttf",    uni=True)
        self.add_font("DejaVu",  "I", "DejaVuSans-Oblique.ttf", uni=True)

    def header(self):
        self.set_font("DejaVu", "I", 8)
        self.set_text_color(130, 130, 130)
        self.cell(0, 8, "IEEE Style Research Paper — Auto Generated", align="C", ln=True)
        self.set_draw_color(180, 180, 180)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(2)

    def footer(self):
        self.set_y(-13)
        self.set_font("DejaVu", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")


def save_pdf(topic, content, images=None):
    """Save a Unicode-safe PDF version."""
    filename = topic.replace(" ", "_") + "_paper.pdf"
    pdf = UnicodePDF()
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()

    pdf.set_font("DejaVu", "B", 16)
    pdf.set_fill_color(10, 10, 60)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 14, topic, fill=True, ln=True, align="C")
    pdf.ln(4)
    pdf.set_text_color(0, 0, 0)

    in_code  = False
    code_buf = []

    def flush_code(lines):
        pdf.set_fill_color(240, 240, 240)
        pdf.set_font("Courier", "", 8)
        pdf.set_text_color(30, 30, 30)
        for cl in lines:
            pdf.multi_cell(0, 5, cl.replace('\t', '    '), fill=True)
        pdf.ln(2)

    for line in content.split('\n'):
        stripped = line.strip()

        if stripped.startswith('```'):
            if not in_code:
                in_code  = True
                code_buf = []
            else:
                in_code = False
                flush_code(code_buf)
            continue

        if in_code:
            code_buf.append(line)
            continue

        if not stripped:
            pdf.ln(2)
            continue

        if re.match(r'^#{1,3} ', stripped) or re.match(r'^[IVX]+\.', stripped):
            heading = re.sub(r'^#{1,3} ', '', stripped).replace('**', '').strip()
            pdf.set_font("DejaVu", "B", 12)
            pdf.set_text_color(10, 10, 60)
            pdf.set_fill_color(220, 225, 255)
            pdf.cell(0, 8, _clean(heading), fill=True, ln=True)
            pdf.set_text_color(0, 0, 0)
            pdf.ln(1)

            if images:
                low = heading.lower()
                if "method" in low and images.get("flowchart"):
                    _insert_pdf_image(pdf, images["flowchart"], "Fig. 1: Methodology Flowchart")
                elif "result" in low and images.get("year_chart"):
                    _insert_pdf_image(pdf, images["year_chart"], "Fig. 2: Papers by Year")
                elif "literature" in low and images.get("graph"):
                    _insert_pdf_image(pdf, images["graph"], "Fig. 3: Citation Graph")

        elif "**" in stripped:
            clean2 = re.sub(r'\*\*(.*?)\*\*', r'\1', stripped)
            pdf.set_font("DejaVu", "B", 10)
            pdf.multi_cell(0, 6, re.sub(r'[*_`#]', '', clean2))

        else:
            pdf.set_font("DejaVu", "", 10)
            pdf.set_text_color(30, 30, 30)
            pdf.multi_cell(0, 6, re.sub(r'[*_`#]', '', stripped))

    pdf.output(filename)
    print(f"📄 PDF saved: {filename}")
    return filename


def _insert_pdf_image(pdf, buf, caption):
    try:
        from PIL import Image
        buf.seek(0)
        img = Image.open(buf)
        tmp = f"_tmp_{caption[:8].replace(' ','_')}.png"
        img.save(tmp)
        pdf.ln(2)
        pdf.image(tmp, x=25, w=160)
        pdf.set_font("DejaVu", "I", 8)
        pdf.set_text_color(80, 80, 80)
        pdf.cell(0, 6, caption, align="C", ln=True)
        pdf.ln(3)
    except Exception as e:
        print(f"Image insert skipped: {e}")


# ═══════════════════════════════════════════════════════════
#  MARKDOWN EXPORT
# ═══════════════════════════════════════════════════════════

def save_markdown(topic, content):
    filename = topic.replace(" ", "_") + "_paper.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"💾 Markdown saved: {filename}")
    return filename
