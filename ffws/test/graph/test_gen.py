#
# (C) 2014-2017 Seiji Matsuoka
# Licensed under the MIT License (MIT)
# http://opensource.org/licenses/MIT
#

import unittest
from ffws.graph import gen


data = {
    "nodes": {"records": [
        {"index": 0, "value": "a"},
        {"index": 1, "value": "b"},
        {"index": 2, "value": "c"}
    ]},
    "edges": {"records": [
        {"source": 0, "target": 1, "weight": 0.5},
        {"source": 0, "target": 2, "weight": 0.8},
        {"source": 1, "target": 2, "weight": 1}
    ]}
}


class TestGen(unittest.TestCase):
    def test_graph_loader(self):
        G = gen.graph_from_json(data, node_fields=["value"])
        self.assertEqual(len(G), 3)
        self.assertEqual(G.nodes[0]["value"], "a")
        self.assertEqual(G[0][2]["weight"], 0.8)

    def test_threshold_network(self):
        G = gen.graph_from_json(data)
        H = gen.threshold_network(G, 0.6)
        self.assertEqual(G[0][1]["weight"], 0.5)
        self.assertEqual(H.number_of_edges(), 2)
