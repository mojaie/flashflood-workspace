#
# (C) 2014-2017 Seiji Matsuoka
# Licensed under the MIT License (MIT)
# http://opensource.org/licenses/MIT
#

import unittest

from ffws.parser import LightCycler480 as lc


class TestLightCycler480(unittest.TestCase):
    def test_file_loader(self):
        data = lc.file_loader("./raw/instruments/LightCycler480.txt")
        plate1 = data["plates"][0]
        self.assertEqual(plate1["plateId"], "Plate1")
        self.assertEqual(plate1["layerIndex"], 0)
        self.assertEqual(plate1["wellValues"][0], "NaN")
        self.assertEqual(plate1["wellValues"][3], "NaN")
        self.assertEqual(plate1["wellValues"][22], 9.83E-1)
        self.assertEqual(plate1["wellValues"][361], 1.98E3)
        self.assertEqual(plate1["wellValues"][383], "NaN")
