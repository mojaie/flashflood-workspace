#
# (C) 2014-2017 Seiji Matsuoka
# Licensed under the MIT License (MIT)
# http://opensource.org/licenses/MIT
#

import unittest

from ffws.parser import BiacoreT200 as bia


class TestBiacoreT200(unittest.TestCase):
    def test_file_loader(self):
        series = [
            {"conc": 50},
            {"conc": 100},
            {"conc": 200},
            {"conc": 400},
            {"conc": 800}
        ]
        rcds = bia.file_loader(
            "./raw/instruments/BiacoreT200/A1e3_D1e-3_C80000.txt",
            series, 0, 5
        )
        self.assertEqual(len(rcds), 185)
