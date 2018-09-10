#
# (C) 2014-2017 Seiji Matsuoka
# Licensed under the MIT License (MIT)
# http://opensource.org/licenses/MIT
#

import unittest

from tornado.testing import AsyncTestCase, gen_test

from flashflood.core.task import Task
from contrib.screenerapi.workflow.compound import Compound


class TestWorkflow(AsyncTestCase):
    @gen_test
    def test_compound(self):
        wf = Compound({"qcsRefIds": "QCS-1504"})
        wf.interval = 0.01
        task = Task(wf)
        yield task.execute()
        self.assertEqual(len(wf.results.records), 18)


if __name__ == '__main__':
    unittest.main()
