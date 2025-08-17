# handlers/network.py
import base64
import io
import networkx as nx
import matplotlib
matplotlib.use("Agg")  # Use headless backend for server
import matplotlib.pyplot as plt
import pandas as pd
from fastapi import APIRouter

def plot_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)
    return encoded

def analyze_network():
    # Load edges.csv
    df = pd.read_csv("edges.csv")
    G = nx.Graph()
    for _, row in df.iterrows():
        G.add_edge(row["source"], row["target"])

    # Calculations
    edge_count = G.number_of_edges()
    degree_dict = dict(G.degree())
    highest_degree_node = max(degree_dict, key=degree_dict.get)
    average_degree = sum(degree_dict.values()) / len(degree_dict)
    density = nx.density(G)
    shortest_path_alice_eve = nx.shortest_path_length(G, source="Alice", target="Eve")

    # Plot network graph
    fig1, ax1 = plt.subplots()
    pos = nx.spring_layout(G, seed=42)
    nx.draw(
        G, pos, with_labels=True, node_color="lightblue",
        edge_color="gray", font_weight="bold", ax=ax1
    )
    network_graph = plot_to_base64(fig1)

    # Degree histogram
    fig2, ax2 = plt.subplots()
    degrees = list(dict(G.degree()).values())
    ax2.bar(range(len(degrees)), degrees, color="green", edgecolor="black")
    ax2.set_xlabel("Node Index")
    ax2.set_ylabel("Degree")
    ax2.set_title("Degree Distribution")
    degree_histogram = plot_to_base64(fig2)

    # Return JSON
    return {
        "edge_count": int(edge_count),
        "highest_degree_node": str(highest_degree_node),
        "average_degree": float(round(average_degree, 2)),
        "density": float(round(density, 2)),
        "shortest_path_alice_eve": int(shortest_path_alice_eve),
        "network_graph": network_graph,
        "degree_histogram": degree_histogram
    }

# FastAPI router for eval system
def fastapi_router():
    router = APIRouter()

    @router.post("/analyze-network")
    def analyze_network_endpoint():
        return analyze_network()

    return router

# Handler for default endpoint style
def handler(request):
    return analyze_network()
