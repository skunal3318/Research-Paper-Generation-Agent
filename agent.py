from search import search_papers, format_papers
from generator import generate_paper
from exporter import save_markdown, save_pdf

def run_agent():
    print("RESEARCH PAPER GENERATION AGENT")

    topic = input("\nENTER YOUR RESEARCH TOPIC: ")

    papers = search_papers(topic)
    context = format_papers(papers)

    print("\n Papers found : ")
    for i,p in enumerate(papers, 1):
        print(f"  {i}, {p['title']} ({p['year']})")

    paper_draft = generate_paper(topic, context)
    # save_paper(topic, paper_draft)
    save_markdown(topic, paper_draft)
    save_pdf(topic, paper_draft)

    print("\n Paper saved...")


if __name__ == "__main__":
    run_agent()