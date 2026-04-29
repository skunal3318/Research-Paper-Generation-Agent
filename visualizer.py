import io
import re
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx


def generate_methodology_flowchart(topic):
    """Generate a methodology flowchart for the topic."""
    fig, ax = plt.subplots(figsize=(6, 8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_facecolor("#f8f9ff")
    fig.patch.set_facecolor("#f8f9ff")

    steps = [
        ("Problem Definition",     "#4A90D9"),
        ("Literature Review",      "#5BA85A"),
        ("Data Collection",        "#E8A838"),
        ("Proposed Methodology",   "#9B59B6"),
        ("Experimentation",        "#E74C3C"),
        ("Results & Analysis",     "#1ABC9C"),
        ("Conclusion",             "#E67E22"),
    ]

    box_w, box_h = 6, 0.7
    x = 2
    y_start = 9.0
    gap = 1.1

    for i, (label, color) in enumerate(steps):
        y = y_start - i * gap
        rect = mpatches.FancyBboxPatch(
            (x, y - box_h / 2), box_w, box_h,
            boxstyle="round,pad=0.1",
            linewidth=1.5,
            edgecolor="white",
            facecolor=color,
        )
        ax.add_patch(rect)
        ax.text(x + box_w / 2, y, label,
                ha="center", va="center",
                fontsize=10, fontweight="bold", color="white")

        if i < len(steps) - 1:
            ax.annotate("",
                xy=(x + box_w / 2, y - box_h / 2 - 0.05),
                xytext=(x + box_w / 2, y - box_h / 2 - 0.35),
                arrowprops=dict(arrowstyle="->", color="#333333", lw=1.5)
            )

    ax.set_title(f"Methodology Flowchart\n{topic}",
                 fontsize=12, fontweight="bold", pad=10, color="#222")

    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", dpi=150)
    plt.close()
    buf.seek(0)
    return buf


def generate_citation_graph(papers):
    """Generate a citation/topic graph from found papers."""
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.set_facecolor("#f8f9ff")
    fig.patch.set_facecolor("#f8f9ff")

    G = nx.Graph()

    central = "Topic"
    G.add_node(central)

    for i, p in enumerate(papers[:8]):
        short = p["title"][:30] + "..." if len(p["title"]) > 30 else p["title"]
        node  = f"P{i+1}: {short}"
        G.add_node(node)
        G.add_edge(central, node)

    pos = nx.spring_layout(G, seed=42, k=2)

    nx.draw_networkx_edges(G, pos, ax=ax,
                           edge_color="#aaaaaa", width=1.5, alpha=0.7)


    nx.draw_networkx_nodes(G, pos, ax=ax,
                           nodelist=[central],
                           node_color="#E74C3C",
                           node_size=1800)

    paper_nodes = [n for n in G.nodes if n != central]
    nx.draw_networkx_nodes(G, pos, ax=ax,
                           nodelist=paper_nodes,
                           node_color="#4A90D9",
                           node_size=1000)

    nx.draw_networkx_labels(G, pos, ax=ax,
                            font_size=6,
                            font_color="white",
                            font_weight="bold")

    ax.set_title("Related Papers Citation Graph",
                 fontsize=12, fontweight="bold", color="#222")
    ax.axis("off")

    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", dpi=150)
    plt.close()
    buf.seek(0)
    return buf


def generate_year_distribution(papers):
    """Bar chart of papers by publication year."""
    from collections import Counter

    years = [p["year"] for p in papers if p["year"] != "N/A"]
    if not years:
        return None

    counts  = Counter(years)
    sorted_years = sorted(counts.keys())
    values  = [counts[y] for y in sorted_years]

    fig, ax = plt.subplots(figsize=(7, 4))
    fig.patch.set_facecolor("#f8f9ff")
    ax.set_facecolor("#f8f9ff")

    bars = ax.bar(sorted_years, values,
                  color="#4A90D9", edgecolor="white",
                  linewidth=1.2, width=0.5)

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.05,
                str(val),
                ha="center", va="bottom",
                fontsize=10, fontweight="bold", color="#333")

    ax.set_xlabel("Publication Year", fontsize=11)
    ax.set_ylabel("Number of Papers",  fontsize=11)
    ax.set_title("Papers by Publication Year", fontsize=12, fontweight="bold")
    ax.spines[["top", "right"]].set_visible(False)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", dpi=150)
    plt.close()
    buf.seek(0)
    return buf
