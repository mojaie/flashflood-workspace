
import glob

from tornado.ioloop import IOLoop

from kiwiii.core.workflow import Workflow
from kiwiii.node.function.apply import Apply
from kiwiii.node.function.number import Number
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
            e2, = self.add_node(Stack(e1, ["compoundID"]))
            es.append(e2)
        es1, = self.add_node(MergeRecords(es))
        # TODO: delete '_field' field
        es2, = self.add_node(Apply(
            es1, datatype,
            fields=[
                {"key": "assayID"},
                {"key": "field"},
                {"key": "valueType"}
            ],
            params={
                "id": "exp_results", "table": "RESULTS",
                "name": "Experiment results",
                "description": "Demo dataset"
            }
        ))
        es3, = self.add_node(Number(es2, field={"key": "id"}))
        self.add_node(SQLiteWriter([es3], self, self.params["file"]))


if __name__ == '__main__':
    wf = ExperimentDataDemo()
    IOLoop.current().run_sync(wf.submit)
    print("done")
