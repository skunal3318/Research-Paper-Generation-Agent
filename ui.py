import streamlit as st
from exporter import save_pdf, save_markdown, save_ieee_docx
from search     import search_papers, format_papers
from generator  import generate_paper
from exporter   import save_pdf, save_markdown

from visualizer import generate_all_visuals

ARXIV_MAX_RESULTS = 12
ARXIV_URL         = "https://export.arxiv.org/api/query"


def main():
    st.set_page_config(
        page_title="IEEE Research Paper Agent",
        page_icon="📄",
        layout="wide"
    )

    # Header
    st.markdown("""
        <h1 style='text-align:center; color:#0a0a3c;'>
            IEEE Research Paper Generation Agent
        </h1>
        <p style='text-align:center; color:#555;'>
        </p>
        <hr>
    """, unsafe_allow_html=True)

    # ── Sidebar ──
    with st.sidebar:
        st.header("Settings")
        num_papers = st.slider("Papers to fetch", 5, 15, ARXIV_MAX_RESULTS)
        show_code  = st.toggle("Show code snippets",  value=True)
        show_figs  = st.toggle("Show diagrams & graphs", value=True)
        st.divider()

    # ── Main input ──
    topic = st.text_input(" Enter your research topic:",
                          placeholder="e.g. Humanoid Robots, Agentic AI, SLAM...")

    if st.button(" Generate IEEE Paper", use_container_width=True, type="primary"):
        if not topic.strip():
            st.warning("Please enter a topic.")
            return

        with st.spinner("Searching arXiv..."):
            papers = search_papers(topic, max_results=num_papers)

        if papers:
            st.success(f"Found {len(papers)} papers!")
            with st.expander("View found papers"):
                for i, p in enumerate(papers, 1):
                    st.markdown(f"**{i}. {p['title']}** ({p['year']})")
                    st.caption(", ".join(p['authors'][:3]))
        else:
            st.info("No papers found — using LLM knowledge.")

        visuals = {}
        if show_figs:
            with st.spinner("Generating all figures..."):
                visuals = generate_all_visuals(topic, papers)

        # ── Generate paper ──
        with st.spinner("Writing IEEE paper (~15 seconds)..."):
            context = format_papers(papers)
            content = generate_paper(topic, context)

        st.success(" Paper ready!")
        st.divider()

        st.markdown("##  IEEE Paper Preview")

        in_code = False
        code_buf = []

        for line in content.split("\n"):
            stripped = line.strip()

            if stripped.startswith("```"):
                if not in_code:
                    in_code  = True
                    code_buf = []
                else:
                    in_code = False
                    if show_code:
                        st.code("\n".join(code_buf), language="python")
                continue

            if in_code:
                code_buf.append(line)
                continue

    
            if stripped.startswith("## ") or stripped.startswith("# "):
                heading = stripped.lstrip("#").strip()
                st.markdown(f"""
                    <div style='background:#0a0a3c; color:white;
                                padding:6px 12px; border-radius:4px;
                                margin-top:16px; font-weight:bold;'>
                        {heading}
                    </div>
                """, unsafe_allow_html=True)

                if show_figs and visuals:
                    low = heading.lower()
                    if "introduction" in low and visuals.get("architecture"):
                        st.image(visuals["architecture"],
                                 caption="Fig. 1: System Architecture",
                                 use_container_width=True)
                    elif "methodology" in low or "proposed" in low:
                        if visuals.get("flowchart"):
                            st.image(visuals["flowchart"],
                                     caption="Fig. 2: Methodology Flowchart",
                                     use_container_width=True)
                    elif "result" in low or "experiment" in low:
                        if visuals.get("comparison"):
                            st.image(visuals["comparison"],
                                     caption="Fig. 3: Performance Comparison",
                                     use_container_width=True)
                        if visuals.get("training"):
                            st.image(visuals["training"],
                                     caption="Fig. 4: Training Curves",
                                     use_container_width=True)
                    elif "related" in low or "literature" in low:
                        if visuals.get("graph"):
                            st.image(visuals["graph"],
                                     caption="Fig. 5: Citation Network",
                                     use_container_width=True)
                        if visuals.get("year_chart"):
                            st.image(visuals["year_chart"],
                                     caption="Fig. 6: Papers by Year",
                                     use_container_width=True)

            elif stripped:
                st.markdown(stripped)

        st.divider()

        st.markdown("### Download")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.download_button(
                "Markdown",
                data=content,
                file_name=f"{topic.replace(' ','_')}_paper.md",
                mime="text/markdown",
                use_container_width=True
            )

        with col2:
            with st.spinner("Building PDF..."):
                pdf_path  = save_pdf(topic, content, images=visuals)
                pdf_bytes = open(pdf_path, "rb").read()
            st.download_button(
                "PDF",
                data=pdf_bytes,
                file_name=f"{topic.replace(' ','_')}_paper.pdf",
                mime="application/pdf",
                use_container_width=True
            )

        
        with col3:
            with st.spinner("Building IEEE DOCX..."):
                docx_path = save_ieee_docx(
                    topic,
                    content,
                    authors="Kunal Yadav",
                    images=visuals
                )
            if docx_path:
                docx_bytes = open(docx_path, "rb").read()
                st.download_button(
                    " IEEE Word (.docx)",
                    data=docx_bytes,
                    file_name=f"{topic.replace(' ','_')}_IEEE_paper.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )


if __name__ == "__main__":
    main()
