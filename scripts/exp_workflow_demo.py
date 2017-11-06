
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
        self.params = {
            "domain": "activity",
            "type": "sqlite",
            "file": "./resources/exp_results_demo.sqlite3",
            "description": "Default SQLite chemical database",
            "resources": [{
                "id": "testdata", "table": "TEST",
                "name": "Test data",
                "description": "Demo dataset",
                "fields": [
                    {"key": "_index"},
                    {"key": "compoundID"},
                    {"key": "assayID"},
                    {"key": "field"},
                    {"key": "valueType"},
                    {"key": "value"}
                ]
            }]
        }
        es = []
        for in_file in glob.glob("./raw/exp_results_demo/*.txt"):
            e1, = self.add_node(CSVFileInput(in_file, delimiter="\t"))
            e2, = self.add_node(Stack(e1, "id"))
            e3, = self.add_node(Apply(e2, datatype))
            es.append(e3)
        merged, = self.add_node(MergeRecords(es))
        self.add_node(SQLiteWriter([merged], self, self.params["file"]))


if __name__ == '__main__':
    wf = ExperimentDataDemo()
    IOLoop.current().run_sync(wf.submit)
    print("done")
