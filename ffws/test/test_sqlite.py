#
# (C) 2014-2017 Seiji Matsuoka
# Licensed under the MIT License (MIT)
# http://opensource.org/licenses/MIT
#

import unittest

from flashflood.interface.sqlite import Connection


class TestSQLite(unittest.TestCase):
    def setUp(self):
        self.conn = Connection("./resources/chem_data_demo.sqlite3")

    def test_columns(self):
        cols = self.conn.columns("DRUGBANKFDA")
        self.assertEqual(len(cols), 5)

    def test_rows_iter(self):
        res = self.conn.rows_iter("DRUGBANKFDA")
        self.assertEqual(sum(1 for r in res), 1543)

    def test_rows_count(self):
        cnt = self.conn.rows_count("DRUGBANKFDA")
        self.assertEqual(cnt, 1543)

    def test_find_first(self):
        res = self.conn.find_first("DRUGBANKFDA", "compound_id", "DB00928")
        self.assertEqual(res["name"], "Azacitidine")
        res = self.conn.find_first("DRUGBANKFDA", "compound_id", "DB00000")
        self.assertEqual(res, None)

    def test_find_iter(self):
        res = self.conn.find_all("DRUGBANKFDA", "compound_id", "DB00928", "=")
        self.assertEqual(next(res)["name"], "Azacitidine")


if __name__ == '__main__':
    unittest.main()
