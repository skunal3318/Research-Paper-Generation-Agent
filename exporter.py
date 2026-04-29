import re
import json
import subprocess
import tempfile
import os
from fpdf import FPDF


def _extract_abstract(content):
    """Pull out the abstract text from the generated paper."""
    lines  = content.split('\n')
    in_abs = False
    buf    = []
    for line in lines:
        stripped = line.strip()
        if re.search(r'abstract', stripped, re.IGNORECASE) and stripped.startswith('#'):
            in_abs = True
            continue
        if in_abs:
            if stripped.startswith('#') or re.match(r'^[IVX]+\.', stripped):
                break
            if stripped:
                buf.append(stripped)
    return ' '.join(buf)


def save_ieee_docx(topic, content, authors="Research Agent"):
    """
    Generate a proper IEEE-formatted .docx using generate_ieee.js.
    Returns the filename.
    """
    filename = topic.replace(" ", "_") + "_IEEE_paper.docx"

    payload = {
        "topic":         topic,
        "authors":       authors,
        "abstract_text": _extract_abstract(content),
        "content":       content,
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json',
                                     delete=False, encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False)
        tmp_in = f.name

    try:
        result = subprocess.run(
            ['node', 'generate_ieee.js', tmp_in, filename],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            print(f" DOCX generation failed:\n{result.stderr}")
            return None
        print(f" IEEE DOCX saved: {filename}")
        return filename
    finally:
        os.unlink(tmp_in)


class UnicodePDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_font("DejaVu",  "",  "DejaVuSans.ttf",          uni=True)
        self.add_font("DejaVu",  "B", "DejaVuSans-Bold.ttf",      uni=True)
        self.add_font("DejaVu",  "I", "DejaVuSans-Oblique.ttf",   uni=True)

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
    """Save a PDF version of the paper (Unicode-safe)."""
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

    in_code   = False
    code_buf  = []

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
            pdf.cell(0, 8, heading, fill=True, ln=True)
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
            clean = re.sub(r'\*\*(.*?)\*\*', r'\1', stripped)
            pdf.set_font("DejaVu", "B", 10)
            pdf.multi_cell(0, 6, re.sub(r'[*_`#]', '', clean))

        else:
            pdf.set_font("DejaVu", "", 10)
            pdf.set_text_color(30, 30, 30)
            pdf.multi_cell(0, 6, re.sub(r'[*_`#]', '', stripped))

    pdf.output(filename)
    print(f" PDF saved: {filename}")
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


def save_markdown(topic, content):
    """Save paper as .md file."""
    filename = topic.replace(" ", "_") + "_paper.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Markdown saved: {filename}")
    return filename
