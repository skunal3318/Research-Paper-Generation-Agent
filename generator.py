from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL

client = Groq(api_key=GROQ_API_KEY)

def _call(system, user, tokens=4000):
    """Single Groq API call."""
    r = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system",  "content": system},
            {"role": "user",    "content": user}
        ],
        max_tokens=tokens,
        temperature=0.7
    )
    return r.choices[0].message.content


def generate_paper(topic, papers_context):
    print("\nGenerating paper in sections...")

    SYSTEM = """You are a senior IEEE researcher with 20+ years of experience.
You write comprehensive, technically rigorous research papers.
Use formal academic language, cite works properly, include equations where relevant,
and write with the depth expected in top-tier IEEE journals."""

    # ── 1. Abstract ───────────────────────────────────────
    print("   [1/7] Abstract...")
    abstract = _call(SYSTEM, f"""
Write a comprehensive IEEE-style abstract for a research paper on: "{topic}"

Related papers found:
{papers_context}

Requirements:
- Exactly 200-250 words
- Cover: motivation, problem statement, proposed approach, key results, significance
- Use passive voice and formal IEEE language
- Include 3-4 specific technical contributions
- End with a statement on broader impact

Output ONLY the abstract text, no heading.
""", tokens=600)

    # ── 2. Introduction ───────────────────────────────────
    print("   [2/7] Introduction...")
    introduction = _call(SYSTEM, f"""
Write a detailed IEEE-style Introduction section for a research paper on: "{topic}"

Related papers:
{papers_context}

Requirements:
- 500-600 words minimum
- Paragraph 1: Broad context and importance of the field
- Paragraph 2: Specific problem being addressed, with technical details
- Paragraph 3: Limitations of existing approaches (cite the related papers above)
- Paragraph 4: Proposed approach and key innovations
- Paragraph 5: Summary of contributions as a numbered list (at least 4 contributions)
- Paragraph 6: Paper organization ("The rest of this paper is organized as follows...")
- Use IEEE citation style [1], [2], etc. referencing the papers above

Output ONLY the section content, no heading.
""", tokens=1200)

    # ── 3. Literature Review ──────────────────────────────
    print("   [3/7] Literature Review...")
    lit_review = _call(SYSTEM, f"""
Write an in-depth IEEE Literature Review / Related Work section for: "{topic}"

Papers to cite and discuss:
{papers_context}

Requirements:
- 600-800 words
- Group papers into 3-4 thematic subsections (use A., B., C. format)
- Each subsection covers a different aspect/approach in the field
- For each paper: summarize approach, results, and limitations
- End with a comparison table described in text: "Table I compares..."
- Identify clear research gaps that your paper addresses
- Use IEEE citation format [1], [2], etc.

Output ONLY the section content with subsection labels.
""", tokens=1500)

    # ── 4. Methodology ────────────────────────────────────
    print("   [4/7] Methodology...")
    methodology = _call(SYSTEM, f"""
Write a detailed IEEE Methodology / Proposed System section for: "{topic}"

Requirements:
- 700-900 words
- Start with a system overview paragraph referencing "Fig. 1" (the architecture diagram)
- Subsection A: System Architecture — describe all components in detail
- Subsection B: Core Algorithm — explain the technical approach step by step
  Include a Python code snippet showing the key algorithm (15-25 lines)
- Subsection C: Implementation Details — datasets, tools, frameworks, parameters
- Include at least one mathematical equation in LaTeX-style notation
  e.g., Loss = (1/N) * Σ(y_i - ŷ_i)²
- Reference "Fig. 2" for the flowchart

Output ONLY the section content with subsection labels.
""", tokens=1500)

    # ── 5. Results & Discussion ───────────────────────────
    print("   [5/7] Results & Discussion...")
    results = _call(SYSTEM, f"""
Write a detailed IEEE Results and Discussion section for: "{topic}"

Requirements:
- 600-700 words
- Subsection A: Experimental Setup — hardware specs, dataset details, baselines
- Subsection B: Quantitative Results — present specific numbers and improvements
  Reference "Table II" for comparison results
  Reference "Fig. 3" for the performance comparison bar chart
  Reference "Fig. 4" for the accuracy/loss graph
  Include realistic metrics: accuracy %, F1 score, precision, recall, latency ms
  Example: "Our method achieves 94.7% accuracy, outperforming [2] by 6.3%"
- Subsection C: Qualitative Analysis — discuss WHY the results are better
- Subsection D: Ablation Study — effect of removing each component
- End with a discussion of limitations

Output ONLY the section content with subsection labels.
""", tokens=1500)

    # ── 6. Conclusion ─────────────────────────────────────
    print("   [6/7] Conclusion...")
    conclusion = _call(SYSTEM, f"""
Write an IEEE Conclusion section for a research paper on: "{topic}"

Requirements:
- 250-300 words
- Paragraph 1: Summary of the problem and proposed approach
- Paragraph 2: Restate key contributions and results with specific numbers
- Paragraph 3: Broader implications and real-world applications
- Paragraph 4: Future work directions (at least 4 specific directions)
- Do NOT use phrases like "In conclusion" or "To summarize"

Output ONLY the section content, no heading.
""", tokens=600)

    # ── 7. References ─────────────────────────────────────
    print("   [7/7] References...")
    references = _call(SYSTEM, f"""
Generate a proper IEEE reference list for a paper on: "{topic}"

Include these papers from arXiv search results:
{papers_context}

Requirements:
- Format EVERY reference in strict IEEE style:
  [N] A. Author, B. Author, "Title of paper," Journal/Conference, vol. X, pp. XX-XX, Year.
- Include all papers from the search results above
- Add 5-6 additional realistic references relevant to {topic}
  (standard textbooks, seminal papers in the field)
- Number sequentially [1], [2], ...
- At least 12 references total

Output ONLY the numbered reference list.
""", tokens=1000)

    # ── Assemble full paper ───────────────────────────────
    paper = f"""## Abstract
{abstract}

## I. Introduction
{introduction}

## II. Related Work
{lit_review}

## III. Proposed Methodology
{methodology}

## IV. Experimental Results
{results}

## V. Conclusion
{conclusion}

## VI. References
{references}
"""

    print("Paper generation complete!")
    return paper
