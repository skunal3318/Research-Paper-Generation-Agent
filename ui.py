import streamlit as st
from exporter import save_pdf, save_markdown, save_ieee_docx
from search     import search_papers, format_papers
from generator  import generate_paper
from exporter   import save_pdf, save_markdown
from visualizer import (generate_methodology_flowchart,
                        generate_citation_graph,
                        generate_year_distribution)

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
            Searches real arXiv papers · Generates IEEE-style paper · 
            Auto diagrams & graphs · PDF + Markdown export
        </p>
        <hr>
    """, unsafe_allow_html=True)

    # ── Sidebar ──
    with st.sidebar:
        st.header("Settings")
        num_papers = st.slider("📚 Papers to fetch", 5, 15, ARXIV_MAX_RESULTS)
        show_code  = st.toggle("🖥️ Show code snippets",  value=True)
        show_figs  = st.toggle("📊 Show diagrams & graphs", value=True)
        st.divider()
        st.caption("Built with arXiv + Groq LLaMA 3.3")

    # ── Main input ──
    topic = st.text_input(" Enter your research topic:",
                          placeholder="e.g. Humanoid Robots, Agentic AI, SLAM...")

    if st.button(" Generate IEEE Paper", use_container_width=True, type="primary"):
        if not topic.strip():
            st.warning("Please enter a topic.")
            return

        # ── Search ──
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

        images = {}
        if show_figs:
            with st.spinner(" Generating diagrams..."):
                images["flowchart"]  = generate_methodology_flowchart(topic)
                images["graph"]      = generate_citation_graph(papers) if papers else None
                images["year_chart"] = generate_year_distribution(papers) if papers else None

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

            # Code blocks
            if stripped.startswith("```"):
                if not in_code:
                    in_code  = True
                    code_buf = []
                else:
                    in_code = False
                    if show_code:
                        lang = "python"
                        st.code("\n".join(code_buf), language=lang)
                continue

            if in_code:
                code_buf.append(line)
                continue

            # Section headings — insert images after relevant sections
            if stripped.startswith("## ") or stripped.startswith("# "):
                heading = stripped.lstrip("#").strip()
                st.markdown(f"""
                    <div style='background:#0a0a3c; color:white; 
                                padding:6px 12px; border-radius:4px; 
                                margin-top:16px; font-weight:bold;'>
                        {heading}
                    </div>
                """, unsafe_allow_html=True)

                if show_figs and images:
                    low = heading.lower()
                    if "method" in low and images.get("flowchart"):
                        st.image(images["flowchart"],
                                 caption="Fig. 1: Methodology Flowchart",
                                 use_container_width=True)
                    elif "result" in low and images.get("year_chart"):
                        st.image(images["year_chart"],
                                 caption="Fig. 2: Papers by Publication Year",
                                 use_container_width=True)
                    elif "literature" in low and images.get("graph"):
                        st.image(images["graph"],
                                 caption="Fig. 3: Related Papers Citation Graph",
                                 use_container_width=True)

            elif stripped:
                st.markdown(stripped)

        st.divider()

        # ── Downloads ──
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
                pdf_path  = save_pdf(topic, content, images=images)
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
                docx_path = save_ieee_docx(topic, content,
                              authors="Research Agent — SRM Institute")
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
