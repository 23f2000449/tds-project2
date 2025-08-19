import pandas as pd
import networkx as nx
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import base64
from io import BytesIO

def _plot_to_base64(fig, max_kb: int = 100) -> str:
    """Convert matplotlib figure to base64 PNG string under max_kb."""
    try:
        for dpi in (150, 120, 100, 90, 80, 70, 60):
            buf = BytesIO()
            fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight", pad_inches=0.1)
            data = buf.getvalue()
            if len(data) <= max_kb * 1024:
                return base64.b64encode(data).decode("utf-8")
        # If all dpi attempts are larger than max_kb, return the smallest possible
        return base64.b64encode(data).decode("utf-8")
    finally:
        plt.close(fig)  # Ensure the figure is closed to free memory

def analyze_network(csv_path: str) -> dict:
    # Read CSV with edges
    df = pd.read_csv(csv_path)
    
    # Create undirected graph from edges
    G = nx.Graph()
    for _, row in df.iterrows():
        G.add_edge(row["source"], row["target"])
    
    edge_count = G.number_of_edges()
    degree_dict = dict(G.degree())
    highest_degree_node = max(degree_dict, key=degree_dict.get)
    average_degree = sum(degree_dict.values()) / len(degree_dict)
    density = nx.density(G)
    
    # Try getting shortest path between Alice and Eve, else None
    try:
        shortest_path_alice_eve = nx.shortest_path_length(G, source="Alice", target="Eve")
    except nx.NetworkXNoPath:
        shortest_path_alice_eve = None
    except nx.NodeNotFound:
        shortest_path_alice_eve = None
    
    # Draw network graph
    fig1, ax1 = plt.subplots()
    pos = nx.spring_layout(G, seed=42)
    nx.draw(G, pos, with_labels=True, node_color="lightblue", edge_color="gray", font_weight="bold", ax=ax1)
    network_graph = _plot_to_base64(fig1)
    
    # Draw degree histogram with green bars
    fig2, ax2 = plt.subplots()
    degrees = list(degree_dict.values())
    ax2.bar(range(len(degrees)), degrees, color="green", edgecolor="black")
    ax2.set_xlabel("Node Index")
    ax2.set_ylabel("Degree")
    ax2.set_title("Degree Distribution")
    degree_histogram = _plot_to_base64(fig2)
    
    # Assemble output JSON dict
    return {
        "edge_count": int(edge_count),
        "highest_degree_node": str(highest_degree_node),
        "average_degree": round(float(average_degree), 2),
        "density": round(float(density), 2),
        "shortest_path_alice_eve": None if shortest_path_alice_eve is None else int(shortest_path_alice_eve),
        "network_graph": network_graph,
        "degree_histogram": degree_histogram,
    }
