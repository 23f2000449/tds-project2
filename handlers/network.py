# handlers/network.py
import pandas as pd
import networkx as nx
import matplotlib
matplotlib.use("Agg")  # headless backend
import matplotlib.pyplot as plt
import base64
from io import BytesIO

def _plot_to_base64(fig, max_kb: int = 100) -> str:
    """Convert matplotlib figure to base64 PNG under max_kb."""
    for dpi in (120, 100, 90, 80, 70, 60):
        buf = BytesIO()
        fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight", pad_inches=0.1)
        data = buf.getvalue()
        if len(data) <= max_kb * 1024:
            plt.close(fig)
            return base64.b64encode(data).decode("utf-8")
    plt.close(fig)
    return base64.b64encode(data).decode("utf-8")

def analyze_network(csv_path: str) -> dict:
    df = pd.read_csv(csv_path)
    G = nx.Graph()
    for _, row in df.iterrows():
        G.add_edge(row["source"], row["target"])

    edge_count = G.number_of_edges()
    degree_dict = dict(G.degree())
    highest_degree_node = max(degree_dict, key=degree_dict.get)
    average_degree = sum(degree_dict.values()) / len(degree_dict)
    density = nx.density(G)

    try:
        shortest_path_alice_eve = nx.shortest_path_length(G, source="Alice", target="Eve")
    except Exception:
        shortest_path_alice_eve = None

    # --- Network graph ---
    fig1, ax1 = plt.subplots()
    pos = nx.spring_layout(G, seed=42)
    nx.draw(G, pos, with_labels=True, node_color="lightblue", edge_color="gray", font_weight="bold", ax=ax1)
    network_graph = _plot_to_base64(fig1)

    # --- Degree histogram ---
    fig2, ax2 = plt.subplots()
    degrees = list(degree_dict.values())
    ax2.bar(range(len(degrees)), degrees, color="green", edgecolor="black")
    ax2.set_xlabel("Node Index")
    ax2.set_ylabel("Degree")
    ax2.set_title("Degree Distribution")
    degree_histogram = _plot_to_base64(fig2)

    return {
        "edge_count": int(edge_count),
        "highest_degree_node": str(highest_degree_node),
        "average_degree": round(float(average_degree), 2),
        "density": round(float(density), 2),
        "shortest_path_alice_eve": None if shortest_path_alice_eve is None else int(shortest_path_alice_eve),
        "network_graph": network_graph,
        "degree_histogram": degree_histogram,
    }
