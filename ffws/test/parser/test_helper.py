#
# (C) 2014-2017 Seiji Matsuoka
# Licensed under the MIT License (MIT)
# http://opensource.org/licenses/MIT
#

import unittest

from ffws.parser import helper


class TestHelper(unittest.TestCase):
    def test_well_index(self):
        self.assertEqual(helper.well_index("A1"), 0)
        self.assertEqual(helper.well_index("A24"), 23)
        self.assertEqual(helper.well_index("P1"), 360)
        self.assertEqual(helper.well_index("P24"), 383)
        self.assertEqual(helper.well_index("A01"), 0)
        self.assertEqual(helper.well_index("p24"), 383)
