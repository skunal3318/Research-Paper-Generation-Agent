import re
import requests

ARXIV_MAX_RESULTS = 12
ARXIV_URL         = "https://export.arxiv.org/api/query"

def search_papers(topic, max_results=ARXIV_MAX_RESULTS):
    print(f"\n Searching papers on: {topic}")
    url = "https://export.arxiv.org/api/query"
    params = {
        "search_query": f"all:{topic}",
        "start": 0,
        "max_results": max_results
    }

    try:
        response = requests.get(url, params=params, timeout=10)

        entries = response.text.split("<entry>")[1:]
        papers = []

        for entry in entries:
            title_match    = re.search(r"<title>(.*?)</title>",     entry, re.DOTALL)
            abstract_match = re.search(r"<summary>(.*?)</summary>", entry, re.DOTALL)
            year_match     = re.search(r"<published>(.*?)</published>", entry)
            authors        = re.findall(r"<name>(.*?)</name>", entry)

            papers.append({
                "title":    title_match.group(1).strip()    if title_match    else "N/A",
                "abstract": abstract_match.group(1).strip() if abstract_match else "No abstract.",
                "authors":  authors,
                "year":     year_match.group(1)[:4]         if year_match     else "N/A"
            })

        print(f"Found {len(papers)} papers.")
        return papers

    except Exception as e:
        print(f"Search failed: {e}")
        return []


def format_papers(papers):
    if not papers:
        return "No related papers found."

    context = ""
    for i, p in enumerate(papers, 1):
        context += f"""
Paper {i}:
Title: {p['title']}
Authors: {', '.join(p['authors'])}
Year: {p['year']}
Abstract: {p['abstract']}
"""
        return context