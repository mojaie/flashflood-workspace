
import glob
import os

from tornado.ioloop import IOLoop

from kiwiii import static
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
            "file": "exp_results_demo.sqlite3",
            "description": "Default SQLite chemical database"
        }
        merge = MergeRecords()
        for in_file in glob.glob("./raw/exp_results_demo/*.txt"):
            csv_in = CSVFileInput(in_file, delimiter="\t")
            stack = Stack(["compoundID"])
            self.connect(csv_in, stack)
            self.connect(stack, merge)
        split = SplitField(
            "_field", [{"key": "assayID"}, {"key": "field"}], ":")
        extend = Extend(
            "valueType", "field",
            apply_func=lambda x: suggested_type.get(x, "numeric"),
            params={
                "id": "exp_results", "table": "RESULTS",
                "name": "Experiment results",
                "description": "Demo dataset"
            }
        )
        number = Number(name="id")
        writer = SQLiteWriter(
            self, os.path.join(static.SQLITE_BASE_DIR, self.params["file"]))
        self.connect(merge, split)
        self.connect(split, extend)
        self.connect(extend, number)
        self.connect(number, writer)


if __name__ == '__main__':
    wf = ExperimentDataDemo()
    IOLoop.current().run_sync(wf.submit)
    print("done")
