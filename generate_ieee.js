const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  AlignmentType, HeadingLevel, BorderStyle, WidthType, ShadingType,
  Header, Footer, PageNumber, NumberFormat, SectionType,
  VerticalAlign, LevelFormat, UnderlineType
} = require('docx');
const fs = require('fs');

// ── Read content passed from Python ──────────────────────
const inputPath  = process.argv[2];
const outputPath = process.argv[3];
const data       = JSON.parse(fs.readFileSync(inputPath, 'utf8'));
const { topic, content, authors = "Research Agent", abstract_text = "" } = data;

// ── Parse sections from markdown content ─────────────────
function parseSections(text) {
  const lines   = text.split('\n');
  const sections = [];
  let current   = null;

  for (const line of lines) {
    const stripped = line.trim();
    if (!stripped) continue;

    // Section heading
    if (/^#{1,3}\s/.test(stripped) || /^[IVX]+\.\s/.test(stripped)) {
      if (current) sections.push(current);
      const title = stripped.replace(/^#{1,3}\s/, '').replace(/\*\*/g, '').trim();
      current = { title, lines: [] };
    } else if (current) {
      current.lines.push(stripped);
    } else {
      // Before first heading — could be abstract
      if (!current) {
        current = { title: '', lines: [stripped] };
      }
    }
  }
  if (current) sections.push(current);
  return sections;
}

// ── Helper: clean markdown symbols ───────────────────────
function clean(text) {
  return text.replace(/\*\*(.*?)\*\*/g, '$1')
             .replace(/[*_`]/g, '')
             .trim();
}

// ── Helper: make a body text paragraph ───────────────────
function bodyPara(text, opts = {}) {
  return new Paragraph({
    alignment: AlignmentType.JUSTIFIED,
    spacing: { after: 60, line: 240 },
    ...opts,
    children: [
      new TextRun({
        text: clean(text),
        font: "Times New Roman",
        size: 20,   // 10pt
        bold: opts.bold || false,
        italics: opts.italics || false,
      })
    ]
  });
}

// ── Helper: section heading (IEEE style) ─────────────────
function sectionHeading(text, roman) {
  return new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 120, after: 60 },
    children: [
      new TextRun({
        text: `${roman}. ${text.toUpperCase()}`,
        font: "Times New Roman",
        size: 20,
        bold: true,
        smallCaps: false,
      })
    ]
  });
}

// ── Helper: subsection heading ────────────────────────────
function subsectionHeading(text) {
  return new Paragraph({
    spacing: { before: 80, after: 40 },
    children: [
      new TextRun({
        text: clean(text),
        font: "Times New Roman",
        size: 20,
        bold: true,
        italics: true,
      })
    ]
  });
}

// ── Helper: code block ────────────────────────────────────
function codePara(text) {
  return new Paragraph({
    spacing: { after: 0, line: 220 },
    indent: { left: 360 },
    children: [
      new TextRun({
        text: text,
        font: "Courier New",
        size: 16,
        color: "1A1A2E",
      })
    ]
  });
}

// ── Build document children ───────────────────────────────
const sections = parseSections(content);
const bodyChildren = [];

const romanNumerals = ['I','II','III','IV','V','VI','VII','VIII','IX','X'];
let sectionCount = 0;

// Process each section
for (const sec of sections) {
  if (sec.title) {
    const roman = romanNumerals[sectionCount] || String(sectionCount + 1);
    sectionCount++;
    bodyChildren.push(sectionHeading(sec.title, roman));
  }

  let inCode = false;
  let codeLines = [];

  for (const line of sec.lines) {
    if (line.startsWith('```')) {
      if (!inCode) {
        inCode = true;
        codeLines = [];
      } else {
        inCode = false;
        for (const cl of codeLines) {
          bodyChildren.push(codePara(cl.replace(/\t/g, '    ')));
        }
        bodyChildren.push(new Paragraph({ spacing: { after: 60 } }));
      }
      continue;
    }

    if (inCode) {
      codeLines.push(line);
      continue;
    }

    if (!line.trim()) continue;

    // Sub-heading inside section (line starting with A. or B.)
    if (/^[A-Z]\.\s/.test(line)) {
      bodyChildren.push(subsectionHeading(line));
    } else {
      bodyChildren.push(bodyPara(line));
    }
  }
}

// ── Full document ─────────────────────────────────────────
const doc = new Document({
  numbering: { config: [] },

  styles: {
    default: {
      document: {
        run: { font: "Times New Roman", size: 20 }
      }
    }
  },

  sections: [
    // ── Section 1: Title + Abstract (single column) ──────
    {
      properties: {
        type: SectionType.CONTINUOUS,
        page: {
          size: { width: 12240, height: 15840 },
          margin: { top: 1008, bottom: 1008, left: 936, right: 936 }
        }
      },
      headers: {
        default: new Header({
          children: [
            new Paragraph({
              alignment: AlignmentType.CENTER,
              border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: "000000" } },
              spacing: { after: 60 },
              children: [
                new TextRun({
                  text: "IEEE Open Journal — Auto-Generated Research Paper",
                  font: "Times New Roman",
                  size: 16,
                  italics: true,
                  color: "444444",
                })
              ]
            })
          ]
        })
      },
      footers: {
        default: new Footer({
          children: [
            new Paragraph({
              alignment: AlignmentType.CENTER,
              border: { top: { style: BorderStyle.SINGLE, size: 6, color: "000000" } },
              children: [
                new TextRun({ text: "Page ", font: "Times New Roman", size: 16 }),
                new TextRun({ children: [PageNumber.CURRENT], font: "Times New Roman", size: 16 })
              ]
            })
          ]
        })
      },
      children: [
        // Paper title
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { after: 120 },
          children: [
            new TextRun({
              text: topic,
              font: "Times New Roman",
              size: 36,   // 18pt
              bold: true,
            })
          ]
        }),

        // Authors
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { after: 60 },
          children: [
            new TextRun({
              text: authors,
              font: "Times New Roman",
              size: 20,
              italics: true,
            })
          ]
        }),

        // Divider
        new Paragraph({
          border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: "000000" } },
          spacing: { after: 120 },
          children: []
        }),

        // Abstract heading
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { before: 80, after: 60 },
          children: [
            new TextRun({
              text: "Abstract",
              font: "Times New Roman",
              size: 20,
              bold: true,
              italics: true,
            })
          ]
        }),

        // Abstract body
        new Paragraph({
          alignment: AlignmentType.JUSTIFIED,
          spacing: { after: 120 },
          indent: { left: 720, right: 720 },
          children: [
            new TextRun({
              text: clean(abstract_text) || `This paper presents a comprehensive study on ${topic}.`,
              font: "Times New Roman",
              size: 18,  // 9pt for abstract
            })
          ]
        }),

        // Divider
        new Paragraph({
          border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: "000000" } },
          spacing: { after: 120 },
          children: []
        }),
      ]
    },

    // ── Section 2: Body (2 columns) ───────────────────────
    {
      properties: {
        type: SectionType.CONTINUOUS,
        page: {
          size: { width: 12240, height: 15840 },
          margin: { top: 1008, bottom: 1008, left: 936, right: 936 }
        },
        column: {
          space: 720,
          count: 2,
          equalWidth: true,
        }
      },
      children: bodyChildren
    }
  ]
});

// ── Write output ──────────────────────────────────────────
Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync(outputPath, buffer);
  console.log(`✅ IEEE DOCX saved: ${outputPath}`);
}).catch(err => {
  console.error('Error:', err);
  process.exit(1);
});
