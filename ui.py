import streamlit as st
from search import search_papers, format_papers
from generator import generate_paper
from exporter import save_pdf
from config import ARXIV_MAX_RESULTS

def main():
    st.set_page_config(
        page_title="Research Paper Agent",
        page_icon="📄",
        layout="centered"
    )

    st.title("🤖 Research Paper Generation Agent")
    st.markdown("Search real papers from **arXiv** and generate a full research paper using **LLaMA 3.3**.")
    st.divider()

    topic = st.text_input("📌 Enter your research topic:", placeholder="e.g. Humanoid Robots, Agentic AI...")
    num_papers = st.slider("📚 Number of papers to fetch:", min_value=5, max_value=15, value=ARXIV_MAX_RESULTS)

    if st.button("🚀 Generate Paper", use_container_width=True):
        if not topic.strip():
            st.warning("Please enter a topic first.")
            return

        with st.spinner("🔍 Searching arXiv..."):
            papers = search_papers(topic, max_results=num_papers)

        if papers:
            st.success(f"Found {len(papers)} papers!")
            with st.expander("View found papers"):
                for i, p in enumerate(papers, 1):
                    st.markdown(f"**{i}. {p['title']}** ({p['year']})")
                    st.caption(", ".join(p['authors'][:3]))
        else:
            st.info("No papers found — generating from LLM knowledge.")

        with st.spinner("Generating paper (~15 seconds)..."):
            context = format_papers(papers)
            content = generate_paper(topic, context)

        st.success("Paper generated!")
        st.divider()
        st.markdown(content)
        st.divider()

        col1, col2 = st.columns(2)

        with col1:
            st.download_button(
                label="Download Markdown",
                data=content,
                file_name=f"{topic.replace(' ', '_')}_paper.md",
                mime="text/markdown",
                use_container_width=True
            )

        with col2:
            pdf_path  = save_pdf(topic, content)
            pdf_bytes = open(pdf_path, "rb").read()
            st.download_button(
                label="Download PDF",
                data=pdf_bytes,
                file_name=f"{topic.replace(' ', '_')}_paper.pdf",
                mime="application/pdf",
                use_container_width=True
            )

if __name__ == "__main__":
    main()