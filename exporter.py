import re
from fpdf import FPDF

class UnicodePDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_font("DejaVu",      "", "DejaVuSans.ttf",      uni=True)
        self.add_font("DejaVu", "B", "DejaVuSans-Bold.ttf", uni=True)

    def header(self):
        pass 

    def footer(self):
        self.set_y(-15)
        self.set_font("DejaVu", "", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")


def save_markdown(topic, content):
    """Save paper as a .md file."""
    filename = topic.replace(" ", "_") + "_paper.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"\nMarkdown saved as: {filename}")
    return filename


def save_pdf(topic, content):
    """Save paper as a formatted .pdf file."""
    filename = topic.replace(" ", "_") + "_paper.pdf"

    pdf = UnicodePDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # ── Cover title bar ──
    pdf.set_font("DejaVu", "B", 16)
    pdf.set_fill_color(30, 30, 30)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 14, f"Research Paper: {topic}", fill=True, ln=True, align="C")
    pdf.ln(5)

    pdf.set_text_color(0, 0, 0)

    for line in content.split("\n"):
        line = line.strip()

        if not line:
            pdf.ln(3)
            continue

        if line.startswith("## ") or (line.startswith("**") and line.endswith("**")):
            heading = line.replace("## ", "").replace("**", "").strip()
            pdf.set_font("DejaVu", "B", 13)
            pdf.set_fill_color(220, 230, 255)
            pdf.set_text_color(0, 0, 100)
            pdf.cell(0, 9, heading, fill=True, ln=True)
            pdf.set_text_color(0, 0, 0)
            pdf.ln(1)

        elif "**" in line:
            clean = re.sub(r"\*\*(.*?)\*\*", r"\1", line)
            clean = re.sub(r"[*_`#]", "", clean)
            pdf.set_font("DejaVu", "B", 11)
            pdf.multi_cell(0, 7, clean)

        else:
            clean = re.sub(r"[*_`#]", "", line)
            pdf.set_font("DejaVu", "", 11)
            pdf.multi_cell(0, 7, clean)

    pdf.output(filename)
    print(f"PDF saved as: {filename}")
    return filename