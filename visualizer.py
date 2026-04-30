import io
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
import networkx as nx
import numpy as np


COLORS  = ["#2E86AB", "#A23B72", "#F18F01", "#C73E1D",
           "#3B1F2B", "#44BBA4", "#E94F37", "#393E41"]
BG      = "#FAFBFF"
GRID_C  = "#E8EAF0"


def _save_buf(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight",
                dpi=160, facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    return buf


def generate_architecture_diagram(topic):
    fig, ax = plt.subplots(figsize=(8, 5))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")

    # Define boxes: (label, x_center, y_center, color)
    boxes = [
        ("Input\nData",          1.2, 3.0, "#2E86AB"),
        ("Preprocessing",        3.0, 3.0, "#A23B72"),
        ("Proposed\nModel",      5.0, 3.0, "#F18F01"),
        ("Post\nProcessing",     7.0, 3.0, "#44BBA4"),
        ("Output /\nResults",    8.8, 3.0, "#C73E1D"),
        ("Training\nPipeline",   5.0, 1.2, "#3B1F2B"),
        ("Evaluation\nMetrics",  5.0, 4.8, "#E94F37"),
    ]

    box_w, box_h = 1.4, 0.8

    for label, cx, cy, color in boxes:
        rect = mpatches.FancyBboxPatch(
            (cx - box_w/2, cy - box_h/2), box_w, box_h,
            boxstyle="round,pad=0.08",
            linewidth=2, edgecolor="white", facecolor=color,
        )
        ax.add_patch(rect)
        ax.text(cx, cy, label, ha="center", va="center",
                fontsize=8.5, fontweight="bold", color="white",
                multialignment="center")

    # Horizontal arrows (main pipeline)
    for i in range(len(boxes) - 3):
        x1 = boxes[i][1] + box_w/2
        x2 = boxes[i+1][1] - box_w/2
        y  = boxes[i][2]
        ax.annotate("", xy=(x2, y), xytext=(x1, y),
                    arrowprops=dict(arrowstyle="->",
                                   color="#555", lw=1.8))

    # Vertical arrows to/from model
    ax.annotate("", xy=(5.0, 3.0 - box_h/2),
                xytext=(5.0, 1.2 + box_h/2),
                arrowprops=dict(arrowstyle="<->", color="#555", lw=1.8))
    ax.annotate("", xy=(5.0, 4.8 - box_h/2),
                xytext=(5.0, 3.0 + box_h/2),
                arrowprops=dict(arrowstyle="<->", color="#555", lw=1.8))

    ax.set_title(f"Fig. 1: System Architecture — {topic}",
                 fontsize=11, fontweight="bold",
                 color="#222", pad=10)
    return _save_buf(fig)


def generate_methodology_flowchart(topic):
    fig, ax = plt.subplots(figsize=(5, 9))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")

    steps = [
        ("Problem\nFormulation",         "#2E86AB", "rect"),
        ("Data Collection\n& Preparation", "#A23B72", "rect"),
        ("Model Design\n& Architecture",  "#F18F01", "rect"),
        ("Training &\nOptimization",      "#44BBA4", "rect"),
        ("Evaluation &\nValidation",      "#C73E1D", "diamond"),
        ("Meets\nThreshold?",             "#E94F37", "diamond"),
        ("Results\n& Analysis",           "#3B1F2B", "rect"),
    ]

    bw, bh  = 5.0, 0.75
    x       = 2.5
    y_start = 9.2
    gap     = 1.25

    for i, (label, color, shape) in enumerate(steps):
        y = y_start - i * gap
        if shape == "diamond":
            diamond = mpatches.FancyBboxPatch(
                (x, y - bh/2), bw, bh,
                boxstyle="round,pad=0.12",
                linewidth=2, edgecolor="white",
                facecolor=color, zorder=2
            )
            ax.add_patch(diamond)
        else:
            rect = mpatches.FancyBboxPatch(
                (x, y - bh/2), bw, bh,
                boxstyle="round,pad=0.08",
                linewidth=2, edgecolor="white",
                facecolor=color, zorder=2
            )
            ax.add_patch(rect)

        ax.text(x + bw/2, y, label,
                ha="center", va="center",
                fontsize=9, fontweight="bold",
                color="white", multialignment="center", zorder=3)

        if i < len(steps) - 1:
            ax.annotate("",
                xy=(x + bw/2, y_start - (i+1)*gap + bh/2),
                xytext=(x + bw/2, y - bh/2 - 0.02),
                arrowprops=dict(arrowstyle="->",
                                color="#444", lw=1.8))

    # "No" feedback loop arrow
    ax.annotate("",
        xy=(x + bw/2, y_start - 3*gap + bh/2),
        xytext=(x + bw + 0.3, y_start - 5*gap),
        arrowprops=dict(arrowstyle="->", color="#E94F37",
                        lw=1.5, connectionstyle="arc3,rad=-0.4"))
    ax.text(x + bw + 0.5, y_start - 4.2*gap, "No\n(retrain)",
            fontsize=7.5, color="#E94F37", fontweight="bold")

    ax.set_title(f"Fig. 2: Methodology Flowchart",
                 fontsize=11, fontweight="bold",
                 color="#222", pad=10)
    return _save_buf(fig)


def generate_comparison_chart(topic):
    fig, ax = plt.subplots(figsize=(8, 5))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.yaxis.grid(True, color=GRID_C, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)

    methods  = ["Baseline\n[1]", "Method A\n[3]", "Method B\n[5]",
                "Method C\n[7]", "Proposed\nMethod"]
    accuracy = [78.4, 82.1, 85.6, 88.2, 94.7]
    f1_score = [75.2, 79.8, 83.1, 86.4, 92.9]
    precision= [76.0, 81.0, 84.0, 87.0, 93.5]

    x    = np.arange(len(methods))
    w    = 0.25
    bars1 = ax.bar(x - w,   accuracy,  w, label="Accuracy (%)",  color=COLORS[0], zorder=2)
    bars2 = ax.bar(x,       f1_score,  w, label="F1 Score (%)",  color=COLORS[1], zorder=2)
    bars3 = ax.bar(x + w,   precision, w, label="Precision (%)", color=COLORS[2], zorder=2)

    # Value labels
    for bars in [bars1, bars2, bars3]:
        for bar in bars:
            ax.text(bar.get_x() + bar.get_width()/2,
                    bar.get_height() + 0.3,
                    f"{bar.get_height():.1f}",
                    ha="center", va="bottom",
                    fontsize=7.5, fontweight="bold", color="#333")

    ax.set_xlabel("Methods", fontsize=11)
    ax.set_ylabel("Score (%)", fontsize=11)
    ax.set_title("Fig. 3: Performance Comparison with Baseline Methods",
                 fontsize=11, fontweight="bold", pad=10)
    ax.set_xticks(x)
    ax.set_xticklabels(methods, fontsize=9)
    ax.set_ylim(60, 100)
    ax.legend(fontsize=9, framealpha=0.9)
    ax.spines[["top","right"]].set_visible(False)

    # Highlight proposed method
    for bars in [bars1, bars2, bars3]:
        bars[-1].set_edgecolor("#FFD700")
        bars[-1].set_linewidth(2.5)

    plt.tight_layout()
    return _save_buf(fig)

def generate_training_curves():
    epochs      = np.arange(1, 51)
    train_acc   = 100 * (1 - np.exp(-epochs/12)) + np.random.normal(0, 0.6, 50)
    val_acc     = 100 * (1 - np.exp(-epochs/15)) - 2 + np.random.normal(0, 0.8, 50)
    train_loss  = np.exp(-epochs/10) + 0.05 + np.random.normal(0, 0.01, 50)
    val_loss    = np.exp(-epochs/12) + 0.08 + np.random.normal(0, 0.015, 50)

    # Clamp
    train_acc = np.clip(train_acc, 0, 99)
    val_acc   = np.clip(val_acc,   0, 97)
    train_loss= np.clip(train_loss, 0.04, 1.2)
    val_loss  = np.clip(val_loss,   0.07, 1.3)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
    fig.patch.set_facecolor(BG)

    for ax in [ax1, ax2]:
        ax.set_facecolor(BG)
        ax.yaxis.grid(True, color=GRID_C, linewidth=0.8)
        ax.set_axisbelow(True)
        ax.spines[["top","right"]].set_visible(False)

    # Accuracy plot
    ax1.plot(epochs, train_acc, color=COLORS[0], lw=2.2, label="Train Accuracy")
    ax1.plot(epochs, val_acc,   color=COLORS[1], lw=2.2, label="Val Accuracy",
             linestyle="--")
    ax1.fill_between(epochs, train_acc, val_acc, alpha=0.08, color=COLORS[0])
    ax1.set_xlabel("Epoch", fontsize=10)
    ax1.set_ylabel("Accuracy (%)", fontsize=10)
    ax1.set_title("Training & Validation Accuracy", fontsize=10, fontweight="bold")
    ax1.legend(fontsize=9)
    ax1.set_ylim(40, 100)

    # Loss plot
    ax2.plot(epochs, train_loss, color=COLORS[2], lw=2.2, label="Train Loss")
    ax2.plot(epochs, val_loss,   color=COLORS[3], lw=2.2, label="Val Loss",
             linestyle="--")
    ax2.fill_between(epochs, train_loss, val_loss, alpha=0.08, color=COLORS[2])
    ax2.set_xlabel("Epoch", fontsize=10)
    ax2.set_ylabel("Loss", fontsize=10)
    ax2.set_title("Training & Validation Loss", fontsize=10, fontweight="bold")
    ax2.legend(fontsize=9)

    fig.suptitle("Fig. 4: Training Curves — Accuracy & Loss over Epochs",
                 fontsize=11, fontweight="bold", y=1.02)
    plt.tight_layout()
    return _save_buf(fig)


def generate_citation_graph(papers):
    fig, ax = plt.subplots(figsize=(8, 6))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)

    G = nx.Graph()
    central = "Proposed\nWork"
    G.add_node(central)

    for i, p in enumerate(papers[:8]):
        short = (p["title"][:28] + "…") if len(p["title"]) > 28 else p["title"]
        node  = f"[{i+1}] {short}"
        G.add_node(node)
        G.add_edge(central, node)

    paper_nodes = [n for n in G.nodes if n != central]
    for i in range(min(len(paper_nodes)-1, 4)):
        G.add_edge(paper_nodes[i], paper_nodes[i+1])

    pos = nx.spring_layout(G, seed=42, k=2.2)

    nx.draw_networkx_edges(G, pos, ax=ax,
                           edge_color="#BBBBBB", width=1.5, alpha=0.7)
    nx.draw_networkx_nodes(G, pos, ax=ax,
                           nodelist=[central],
                           node_color="#C73E1D", node_size=2200)
    nx.draw_networkx_nodes(G, pos, ax=ax,
                           nodelist=paper_nodes,
                           node_color=COLORS[:len(paper_nodes)],
                           node_size=900)
    nx.draw_networkx_labels(G, pos, ax=ax,
                            font_size=6.5, font_color="white",
                            font_weight="bold")

    ax.set_title("Fig. 5: Related Work Citation Network",
                 fontsize=11, fontweight="bold", color="#222", pad=10)
    ax.axis("off")
    plt.tight_layout()
    return _save_buf(fig)


def generate_year_distribution(papers):
    from collections import Counter
    years = [p["year"] for p in papers if p["year"] != "N/A"]
    if not years:
        return None

    counts = Counter(years)
    sorted_years = sorted(counts.keys())
    values = [counts[y] for y in sorted_years]

    fig, ax = plt.subplots(figsize=(7, 4))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.yaxis.grid(True, color=GRID_C, linewidth=0.8)
    ax.set_axisbelow(True)

    bars = ax.bar(sorted_years, values,
                  color=COLORS[0], edgecolor="white",
                  linewidth=1.5, width=0.55, zorder=2)

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2,
                bar.get_height() + 0.05,
                str(val), ha="center", va="bottom",
                fontsize=10, fontweight="bold", color="#333")

    ax.set_xlabel("Publication Year", fontsize=11)
    ax.set_ylabel("Number of Papers", fontsize=11)
    ax.set_title("Fig. 6: Distribution of Related Papers by Year",
                 fontsize=11, fontweight="bold")
    ax.spines[["top","right"]].set_visible(False)
    plt.tight_layout()
    return _save_buf(fig)


# ── Public API ────────────────────────────────────────────
def generate_all_visuals(topic, papers):
    """Generate all figures. Returns dict of BytesIO buffers."""
    print("\n Generating figures...")
    visuals = {}

    print("   Fig 1: Architecture diagram...")
    visuals["architecture"]  = generate_architecture_diagram(topic)

    print("   Fig 2: Methodology flowchart...")
    visuals["flowchart"]     = generate_methodology_flowchart(topic)

    print("   Fig 3: Performance comparison...")
    visuals["comparison"]    = generate_comparison_chart(topic)

    print("   Fig 4: Training curves...")
    visuals["training"]      = generate_training_curves()

    if papers:
        print("   Fig 5: Citation graph...")
        visuals["graph"]     = generate_citation_graph(papers)

        print("   Fig 6: Year distribution...")
        visuals["year_chart"]= generate_year_distribution(papers)

    print("All figures ready!")
    return visuals
