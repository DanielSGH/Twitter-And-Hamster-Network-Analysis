import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import os
import random
from collections import Counter
os.environ["QT_LOGGING_RULES"] = "qt.qpa.wayland=false"

files = ["twitter-small-out.tsv"]

random.seed(42) # for reproducible results

# TODO: add comments, which part of the code belongs to which question
# ABOVE IS NECESSARY FOR THE ASSIGNMENT
for filename in files:
    df = pd.read_csv(filename, sep="\t")
    # G = nx.read_edgelist(filename, delimiter="\t", create_using=nx.DiGraph)
    G = nx.from_pandas_edgelist(df, source="source", target="target", edge_attr="weight", create_using=nx.DiGraph)

    network_name = filename.split('-')[-1]
    print(
        f"{network_name}: "
        f"{G.number_of_edges()} links, "
        f"{G.number_of_nodes()} users, "
        f"density = {nx.density(G):.3e}"
    )

    in_sequence = [d for n, d in G.in_degree()]
    out_sequence = [d for n, d in G.out_degree()]

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.loglog(*np.unique(in_sequence, return_counts=True),
              "o", label="In-degree")
    ax.loglog(*np.unique(out_sequence, return_counts=True),
              "o", label="Out-degree")
    ax.set_title(f"Degree distribution - {network_name}")
    ax.set_xlabel("Degree")
    ax.set_ylabel("Number of Nodes")
    ax.legend()

    fig.tight_layout()
    plt.savefig('degree-distribution.png', dpi=500)

    wcc = list(nx.weakly_connected_components(G))
    largest_wcc = max(wcc, key=len)
    wcc_subgraph = G.subgraph(largest_wcc)

    scc = list(nx.strongly_connected_components(G))
    largest_scc = max(scc, key=len)
    scc_subgraph = G.subgraph(largest_scc)

    U = G.to_undirected()
    U.remove_edges_from(nx.selfloop_edges(U))

    approx = nx.approximation.average_clustering(U, trials=1_000, seed=42)
    print(f"{network_name}: approx average clustering = {approx:.4f}")

    giant = U.subgraph(largest_wcc)

    n_samples = min(1000, giant.number_of_nodes())
    name = filename.split('-')[-1]
    counts = Counter()
    for s in random.sample(list(giant), n_samples):
        counts.update(nx.single_source_shortest_path_length(giant, s).values())

    counts = dict(sorted(counts.items()))

    plt.figure(figsize=(8, 6))
    plt.bar(counts.keys(), counts.values(), label="distance")
    plt.yscale("log")
    plt.xticks(list(counts.keys()))
    plt.title(f"Distance distribution - {name}")
    plt.xlabel("Distance")
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.savefig('distance-distribution.png', dpi=200)

    # average distance: exclude distance 0 (a node paired with itself)
    pairs = {d: c for d, c in counts.items() if d > 0}

    weights, freqs = np.unique(df["weight"], return_counts=True)


        # ---------- Q1.4: centrality (top 20) ----------
    def top20(scores):
        return sorted(scores.items(), key=lambda x: x[1], reverse=True)[:20]

    # degree centrality, directed: in- and outdegree centrality
    indeg_c = nx.in_degree_centrality(G)
    outdeg_c = nx.out_degree_centrality(G)

    # betweenness, approximated with k sampled sources, undirected giant component
    betw = nx.betweenness_centrality(giant, k=min(1000, giant.number_of_nodes()), seed=42)

    # closeness, approximated: BFS from sampled sources, undirected giant component
    sources = random.sample(list(giant), min(1000, giant.number_of_nodes()))
    dist_sum = Counter()
    for s in sources:
        for node, d in nx.single_source_shortest_path_length(giant, s).items():
            dist_sum[node] += d
    closeness = {v: len(sources) / dist_sum[v] for v in giant if dist_sum[v] > 0}

    for name, scores in [("in-degree", indeg_c), ("out-degree", outdeg_c),
                         ("betweenness", betw), ("closeness", closeness)]:
        print(f"\n{network_name}: top 20 by {name}")
        for rank, (user, score) in enumerate(top20(scores), 1):
            print(f"{rank:2d}. {user:20s} {score:.5f}")

    fig3, ax3 = plt.subplots(figsize=(8, 6))
    ax3.loglog(weights, freqs, "o")
    ax3.set_title(f"Link weight distribution - {network_name}")
    ax3.set_xlabel("Link weight (number of mentions)")
    ax3.set_ylabel("Number of links")
    fig3.tight_layout()
    fig3.savefig(f"{network_name}-weights.png", dpi=200)
    
    # print(network_name)
    # print(f"  # weakly connected components:   {len(wcc)}")
    # print(f"  # strongly connected components: {len(scc)}")
    # print(f"  Largest WCC: {wcc_subgraph.number_of_nodes()} nodes, "
    #       f"{wcc_subgraph.number_of_edges()} links")
    # print(f"  Largest SCC: {scc_subgraph.number_of_nodes()} nodes, "
    #       f"{scc_subgraph.number_of_edges()} links")
    # print(f"{name}'s approx average distance in giant component ({n_samples} Samples): {sum(d * c for d, c in pairs.items()) / sum(pairs.values())}")
