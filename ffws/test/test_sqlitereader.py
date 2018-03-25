#
# (C) 2014-2017 Seiji Matsuoka
# Licensed under the MIT License (MIT)
# http://opensource.org/licenses/MIT
#

import unittest

from tornado.testing import AsyncTestCase, gen_test

from flashflood.core.container import Container, Counter
from flashflood.core.task import Task
from flashflood.core.workflow import Workflow
from flashflood.node.chem.molecule import UnpickleMolecule
from flashflood.node.reader import sqlite
from flashflood.node.writer.container import ContainerWriter


class TestSQLiteReader(AsyncTestCase):
    @gen_test
    def test_reader(self):
        wf = Workflow()
        wf.interval = 0.01
        result = Container()
        wf.append(sqlite.SQLiteReader(
            [("./resources/chem_data_demo.sqlite3", "DRUGBANKFDA")]
        ))
        wf.append(ContainerWriter(result))
        task = Task(wf)
        yield task.execute()
        self.assertEqual(len(result.records), 1543)

    @gen_test
    def test_search(self):
        wf = Workflow()
        wf.interval = 0.01
        result = Container()
        counter = Counter()
        wf.append(sqlite.SQLiteReaderSearch(
            [("./resources/chem_data_demo.sqlite3", "DRUGBANKFDA")],
            "name", ("Ritonavir", "", "Ceftazidime", "Quinestrol"),
            counter=counter
        ))
        wf.append(UnpickleMolecule())
        wf.append(ContainerWriter(result))
        task = Task(wf)
        yield task.execute()
        self.assertEqual(counter.value, 4)
        self.assertEqual(len(result.records[0]["__molobj"]), 50)
        self.assertEqual(len(result.records[2]["__molobj"]), 38)
        self.assertEqual(len(result.records[3]["__molobj"]), 30)


if __name__ == '__main__':
    unittest.main()
