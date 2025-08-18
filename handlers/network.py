# handlers/network.py
import pandas as pd
import networkx as nx
import matplotlib
matplotlib.use("Agg")  # headless backend
import matplotlib.pyplot as plt
import base64
from io import BytesIO


def _plot_to_base64(fig, max_kb: int = 100) -> str:
    """Convert matplotlib figure to base64 PNG under max_kb (no prefix)."""
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
    # --- Load CSV into graph ---
    df = pd.read_csv(csv_path)
    G = nx.Graph()
    for _, row in df.iterrows():
        G.add_edge(str(row["source"]), str(row["target"]))

    # --- Metrics ---
    edge_count = G.number_of_edges()
    degree_dict = dict(G.degree())
    highest_degree_node = max(degree_dict, key=degree_dict.get)
    average_degree = 2 * edge_count / G.number_of_nodes()
    density = nx.density(G)

    try:
        shortest_path_alice_eve = nx.shortest_path_length(G, source="Alice", target="Eve")
    except nx.NetworkXNoPath:
        shortest_path_alice_eve = -1

    # --- Network graph plot ---
    fig1, ax1 = plt.subplots()
    pos = nx.spring_layout(G, seed=42)
    nx.draw(
        G, pos,
        with_labels=True,
        node_color="lightblue",
        edge_color="gray",
        font_weight="bold",
        ax=ax1
    )
    network_graph = _plot_to_base64(fig1)

    # --- Degree histogram ---
    fig2, ax2 = plt.subplots()
    degrees = [degree_dict[node] for node in G.nodes()]
    ax2.bar(list(G.nodes()), degrees, color="green", edgecolor="black")
    ax2.set_xlabel("Node")
    ax2.set_ylabel("Degree")
    degree_histogram = _plot_to_base64(fig2)

    # --- Return JSON (must match schema exactly) ---
    return {
        "edge_count": int(edge_count),
        "highest_degree_node": str(highest_degree_node),
        "average_degree": float(average_degree),  # do not round
        "density": float(density),                # do not round
        "shortest_path_alice_eve": int(shortest_path_alice_eve),
        "network_graph": network_graph,
        "degree_histogram": degree_histogram,
    }
