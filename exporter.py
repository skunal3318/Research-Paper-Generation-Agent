import re
import io
from fpdf import FPDF
from PIL import Image


class IEEEPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_font("DejaVu",  "",  "DejaVuSans.ttf",      uni=True)
        self.add_font("DejaVu",  "B", "DejaVuSans-Bold.ttf", uni=True)
        self.add_font("DejaVu",  "I", "DejaVuSans-Oblique.ttf", uni=True)

    def header(self):
        self.set_font("DejaVu", "B", 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, "IEEE Style Research Paper — Auto Generated", align="C", ln=True)
        self.set_draw_color(180, 180, 180)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(2)

    def footer(self):
        self.set_y(-13)
        self.set_font("DejaVu", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")


def _clean(text):
    return re.sub(r"[*_`]", "", text).strip()


def save_markdown(topic, content):
    filename = topic.replace(" ", "_") + "_paper.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"\nMarkdown saved: {filename}")
    return filename


def save_pdf(topic, content, images=None):
    """
    Save IEEE-style PDF.
    images: dict with keys 'flowchart', 'graph', 'year_chart' — each a BytesIO PNG
    """
    filename = topic.replace(" ", "_") + "_paper.pdf"
    pdf = IEEEPDF()
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()

    pdf.set_font("DejaVu", "B", 18)
    pdf.set_text_color(10, 10, 60)
    pdf.multi_cell(0, 10, topic, align="C")
    pdf.ln(1)

    pdf.set_fill_color(10, 10, 60)
    pdf.cell(0, 1, "", fill=True, ln=True)
    pdf.ln(4)

    in_code_block = False
    code_lines    = []

    def flush_code(code_lines):
        """Render a collected code block."""
        pdf.set_fill_color(240, 240, 240)
        pdf.set_draw_color(180, 180, 180)
        pdf.set_font("Courier", "", 8)
        pdf.set_text_color(30, 30, 30)
        for cl in code_lines:
            clean = cl.replace("\t", "    ")
            pdf.multi_cell(0, 5, clean, border=0, fill=True)
        pdf.set_draw_color(180, 180, 180)
        pdf.ln(2)

    for line in content.split("\n"):
        stripped = line.strip()

        if stripped.startswith("```"):
            if not in_code_block:
                in_code_block = True
                code_lines = []
            else:
                in_code_block = False
                flush_code(code_lines)
            continue

        if in_code_block:
            code_lines.append(line)
            continue

        if not stripped:
            pdf.ln(2)
            continue

        if re.match(r"^#{1,3} ", stripped) or re.match(r"^[IVX]+\.", stripped):
            heading = re.sub(r"^#{1,3} ", "", stripped)
            pdf.set_font("DejaVu", "B", 12)
            pdf.set_text_color(10, 10, 60)
            pdf.set_fill_color(220, 225, 255)
            pdf.cell(0, 8, _clean(heading), fill=True, ln=True)
            pdf.set_text_color(0, 0, 0)
            pdf.ln(1)

        
            if images:
                low = heading.lower()
                if "method" in low and "flowchart" in images:
                    _insert_image(pdf, images["flowchart"], "Fig. 1: Methodology Flowchart")
                elif "result" in low and "year_chart" in images:
                    _insert_image(pdf, images["year_chart"], "Fig. 2: Papers by Year")
                elif "literature" in low and "graph" in images:
                    _insert_image(pdf, images["graph"], "Fig. 3: Citation Graph")

        elif "**" in stripped:
            clean = re.sub(r"\*\*(.*?)\*\*", r"\1", stripped)
            pdf.set_font("DejaVu", "B", 10)
            pdf.set_text_color(0, 0, 0)
            pdf.multi_cell(0, 6, _clean(clean))

        else:
            pdf.set_font("DejaVu", "", 10)
            pdf.set_text_color(30, 30, 30)
            pdf.multi_cell(0, 6, _clean(stripped))

    pdf.output(filename)
    print(f"📄 IEEE PDF saved: {filename}")
    return filename


def _insert_image(pdf, buf, caption):
    """Insert a BytesIO PNG image into the PDF."""
    try:
        buf.seek(0)
        img = Image.open(buf)
        tmp = f"_tmp_{caption[:10].replace(' ','_')}.png"
        img.save(tmp)
        pdf.ln(2)
        pdf.image(tmp, x=25, w=160)
        pdf.set_font("DejaVu", "I", 8)
        pdf.set_text_color(80, 80, 80)
        pdf.cell(0, 6, caption, align="C", ln=True)
        pdf.ln(3)
    except Exception as e:
        print(f"Image insert failed: {e}")
