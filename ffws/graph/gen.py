#
# (C) 2014-2017 Seiji Matsuoka
# Licensed under the MIT License (MIT)
# http://opensource.org/licenses/MIT
#

import networkx as nx


def graph_from_json(data, node_fields=(), edge_fields=("weight",)):
    """ load graph JSON file

    Args:
        data: JSON object
        node_fields: node fields to import
        edge_fields: edge fields to import

    Returns:
        networkx.Graph
    """
    G = nx.Graph()
    for node in data["nodes"]["records"]:
        ndata = {k: node[k] for k in node_fields}
        G.add_node(node["index"], **ndata)
    for edge in data["edges"]["records"]:
        edata = {k: edge[k] for k in edge_fields}
        G.add_edge(edge["source"], edge["target"], **edata)
    return G


def threshold_network(G, threshold, weight_field="weight"):
    """ Generate threshold network

    Args:
        G: networkx.Graph
        threshold: network threshold
        weight_field: edge weight field

    Returns:
        threshold network graph which is independent to the original
    """
    to_be_removed = []
    for u, v, edge in G.edges.data():
        if weight_field in edge and edge[weight_field] < threshold:
            to_be_removed.append((u, v))
    H = G.copy()  # Deep copy
    H.remove_edges_from(to_be_removed)
    return H
