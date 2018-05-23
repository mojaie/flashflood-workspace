#
# (C) 2014-2017 Seiji Matsuoka
# Licensed under the MIT License (MIT)
# http://opensource.org/licenses/MIT
#

import math

import networkx as nx


def network_stats(G):
    """ Calculate network properties

    Args:
        G: networkx.Graph
    """
    result = {
        "log_d": math.log10(nx.density(G)),  # Log of network density
        "cc": nx.average_clustering(G),  # Average clustering coefficient
        "transitivity": nx.transitivity(G),
        "deg_assort": None,
        "nonisolated": None
    }
    # Degree assortativity
    if G.number_of_edges() > 3 and nx.density(G) < 1:
        deg_assort = nx.degree_assortativity_coefficient(G)
        if not math.isnan(deg_assort):  # Complete graph results "nan"
            result["deg_assort"] = deg_assort

    # Average path length
    """
    apls = 0
    for g in nx.connected_component_subgraphs(G):
        for node in g:
            path_length = nx.single_source_dijkstra_path_length(g, node)
            apls += sum(path_length.values())
    result["average_path_length"] = apls / (len(G) * (len(G) - 1))
    """
    # Non-isolated node ratio
    iso_cnt = sum(1 for _, d in G.degree if not d)
    result["nonisolated"] = 1 - (iso_cnt / len(G))
    return result
