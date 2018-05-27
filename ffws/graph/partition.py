#
# (C) 2014-2017 Seiji Matsuoka
# Licensed under the MIT License (MIT)
# http://opensource.org/licenses/MIT
#

from collections import Counter

import community


def assignment(G, weight="weight", resolution=1):
    """ Assign community partition to the graph by Louvain method"""
    if G.number_of_edges():
        part = community.best_partition(
            G, weight=weight, resolution=resolution)
        modu = community.modularity(part, G)
    else:
        part = {n: n for n in G.nodes}
        modu = None
    pmap = {}
    for node, p in part.items():
        if p not in pmap:
            pmap[p] = []
        pmap[p].append(node)
    return part, pmap, modu


def stats(G):
    """ Calculate community partition parameters

    Args:
        G: networkx.Graph
    """
    result = {
        "precision": None,
        "recall": None,
        "f_measure": None
    }
    part = {n: p for n, p in G.nodes.data("partition")}
    # Precision, recall and F-measure
    inner_e = 0
    for u, v in G.edges:
        if G.node[u]["partition"] == G.node[v]["partition"]:
            inner_e += 1
    cluster_cnt = Counter(part.values())
    inner_pe = sum([v * (v - 1) / 2 for v in cluster_cnt.values()])
    if G.number_of_edges():
        result["precision"] = prec = inner_e / G.number_of_edges()
    if inner_pe:
        result["recall"] = recall = inner_e / inner_pe
    if prec is not None and recall is not None:
        result["f_measure"] = 2 * prec * recall / (prec + recall)
    return result
