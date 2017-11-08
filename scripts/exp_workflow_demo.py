
import glob

from tornado.ioloop import IOLoop

from kiwiii.core.workflow import Workflow
from kiwiii.node.field.extend import Extend
from kiwiii.node.field.split import SplitField
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


class ExperimentDataDemo(Workflow):
    def __init__(self):
        super().__init__()
        self.params = {
            "domain": "activity",
            "type": "sqlite",
            "file": "./resources/exp_results_demo.sqlite3",
            "description": "Default SQLite chemical database"
        }
        es = []
        for in_file in glob.glob("./raw/exp_results_demo/*.txt"):
            e1, = self.add_node(CSVFileInput(in_file, delimiter="\t"))
            e2, = self.add_node(Stack(e1, ["compoundID"]))
            es.append(e2)
        es1, = self.add_node(MergeRecords(es))
        es2, = self.add_node(SplitField(
            es1, "_field", [{"key": "assayID"}, {"key": "field"}], ":"))
        es3, = self.add_node(Extend(
            es2, "valueType", "field",
            apply_func=lambda x: suggested_type.get(x, "numeric"),
            params={
                "id": "exp_results", "table": "RESULTS",
                "name": "Experiment results",
                "description": "Demo dataset"
            }
        ))
        es4, = self.add_node(Number(es3, name="id"))
        self.add_node(SQLiteWriter([es4], self, self.params["file"]))


if __name__ == '__main__':
    wf = ExperimentDataDemo()
    IOLoop.current().run_sync(wf.submit)
    print("done")
