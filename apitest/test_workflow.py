#
# (C) 2014-2017 Seiji Matsuoka
# Licensed under the MIT License (MIT)
# http://opensource.org/licenses/MIT
#

import unittest

from tornado import gen
from tornado.testing import AsyncTestCase, gen_test

from flashflood.core.task import Task
from flashflood.workflow.db import ChemDBSearch, ChemDBFilter
from flashflood.workflow.chemprop import ChemProp
from flashflood.workflow.gls import GLS
from flashflood.workflow.profile import Profile
from flashflood.workflow.substructure import Substruct


class TestWorkflow(AsyncTestCase):
    @gen_test
    def test_chemdbsearch(self):
        wf = ChemDBSearch({
            "targets": ("drugbankfda",),
            "key": "compound_id",
            "values": ("DB00123", "DB00245", "DB00649")
        })
        wf.interval = 0.01
        task = Task(wf)
        yield task.execute()
        self.assertEqual(len(wf.results.records), 3)

    @gen_test
    def test_chemdbfilter(self):
        wf = ChemDBFilter({
            "targets": ("drugbankfda",),
            "key": "name",
            "value": "%m_cin",
            "operator": "lk"
        })
        wf.interval = 0.01
        task = Task(wf)
        yield task.execute()
        self.assertEqual(len(wf.results.records), 28)

    @gen_test
    def test_chemprop(self):
        wf = ChemProp({
            "targets": ("drugbankfda",),
            "key": "_mw",
            "value": "1500",
            "operator": "gt"
        })
        wf.interval = 0.01
        task = Task(wf)
        yield task.execute()
        self.assertEqual(len(wf.results.records), 9)

    @gen_test
    def test_profile(self):
        wf = Profile({
            "targets": ("exp_results",),
            "compound_id": "DB00189"
        })
        wf.interval = 0.01
        task = Task(wf)
        yield task.execute()
        self.assertEqual(len(wf.results.records), 9)

    @gen_test
    @unittest.skip("")
    def test_substr(self):
        wf = Substruct({
            "targets": ("drugbankfda",),
            "queryMol": {
                "format": "dbid",
                "source": "drugbankfda",
                "value": "DB00193"
            },
            "params": {
                "ignoreHs": "1"
            }
        })
        wf.interval = 0.01
        task = Task(wf)
        task.execute()
        yield gen.sleep(1)
        task.interrupt()
        while task.status != "aborted":
            yield gen.sleep(0.01)
        self.assertEqual(len(wf.results.records), 1)

    @gen_test
    def test_gls(self):
        wf = GLS({
            "targets": ("drugbankfda",),
            "queryMol": {
                "format": "dbid",
                "source": "drugbankfda",
                "value": "DB00193"
            },
            "params": {
                "ignoreHs": "1",
                "measure": "sim",
                "threshold": "0.95",
                "diameter": "8",
                "maxTreeSize": "40",
                "molSizeCutoff": "20"
            }
        })
        wf.interval = 0.01
        task = Task(wf)
        task.execute()
        yield gen.sleep(1)
        task.interrupt()
        while task.status != "aborted":
            yield gen.sleep(0.01)
        self.assertEqual(len(wf.results.records), 1)


if __name__ == '__main__':
    unittest.main()
