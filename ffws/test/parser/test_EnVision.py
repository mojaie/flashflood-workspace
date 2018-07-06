#
# (C) 2014-2018 Seiji Matsuoka
# Licensed under the MIT License (MIT)
# http://opensource.org/licenses/MIT
#

import unittest

from ffws.parser import EnVision as ev


class TestEnVision(unittest.TestCase):
    def test_envision_96well(self):
        data = ev.file_loader("./raw/instruments/EnVision_96well.csv", 8, 12)
        plate1 = data["plates"][0]
        self.assertEqual(plate1["plateId"], "Plate#1")
        self.assertEqual(plate1["layerIndex"], 0)
        self.assertEqual(plate1["wellValues"][0], 40)
        self.assertEqual(plate1["wellValues"][10], 2934)
        self.assertEqual(plate1["wellValues"][84], 41)
        self.assertEqual(plate1["wellValues"][95], "NaN")
        plate2 = data["plates"][1]
        self.assertEqual(plate2["layerIndex"], 1)
        self.assertEqual(plate2["wellValues"][10], 2334)
        self.assertEqual(plate2["wellValues"][94], 128465)
