#
# (C) 2014-2017 Seiji Matsuoka
# Licensed under the MIT License (MIT)
# http://opensource.org/licenses/MIT
#

import unittest

from ffws.graph import entropy


class TestEntropy(unittest.TestCase):
    def test_entropy(self):
        asn = {
            "a": [0, 1],
            "b": [2, 3]
        }
        h = entropy.entropy(asn, 4)
        self.assertEqual(h, 1)
        asn = {
            "a": [0, 1, 2, 3]
        }
        h = entropy.entropy(asn, 4)
        self.assertEqual(h, 0)
        asn = {
            "a": [0], "b": [1], "c": [2], "d": [3]
        }
        h = entropy.entropy(asn, 4)
        self.assertEqual(h, 2)
        w = {0: 1, 1: 0.333, 2: 0.5, 3: 0.5}
        asn = {
            "a": [0], "b": [1], "c": [2], "d": [3],
            "e": [1], "f": [1], "g": [2], "h": [3]
        }
        h = entropy.entropy(asn, 4, weight=w)
        self.assertAlmostEqual(h, 2, 2)
