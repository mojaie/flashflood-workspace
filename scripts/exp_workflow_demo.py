
import glob
import os
import yaml

from tornado.ioloop import IOLoop

from kiwiii.core.workflow import Workflow
from kiwiii.node.function.apply import Apply
from kiwiii.node.io.sqlitewriter import SQLiteWriter
from kiwiii.node.io.csv import CSVFileInput
from kiwiii.node.record.merge import MergeRecords
from kiwiii.node.transform.stack import Stack

csv_options = {
    "delimiter": "\t"
}

suggested_type = {
    "inh": "inhbition%",
    "ic50": "ic50",
    "valid": "flag"
}


def datatype(row):
    row["assayID"], row["field"] = row["_field"].split(":")
    # TODO: suggest by value
    row["valueType"] = suggested_type.get(row["field"], "text")
    del row["_field"]
    return row


class ExperimentDataDemo(Workflow):
    def __init__(self):
        super().__init__()
        es = []
        for in_file in glob.glob("./raw/exp_data_demo/*.txt"):
            name = os.basename(in_file).split(".")[0]
            e1, = CSVFileInput(in_file, name=name, option=csv_options)
            e2 = Stack("id", e1)
            e3 = Apply(datatype, e2)
            es.append(e3)
        merged = MergeRecords(es)
        self.add_node(
            SQLiteWriter(merged, self, "./resources/exp_data_demo.sqlite3"))


if __name__ == '__main__':
    wf = ExperimentDataDemo()
    IOLoop.current().run_sync(wf.submit)
