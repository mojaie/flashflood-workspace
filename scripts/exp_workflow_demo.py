
import glob
import os

from tornado.ioloop import IOLoop

from flashflood import configparser as conf
from flashflood import static
from flashflood.core.task import Task
from flashflood.core.workflow import Workflow
from flashflood.node.field.extend import Extend
from flashflood.node.field.split import SplitField
from flashflood.node.field.update import UpdateFields
from flashflood.node.reader.csv import CSVFileReader
from flashflood.node.record.merge import MergeRecords
from flashflood.node.transform.stack import Stack
from flashflood.node.writer.sqlite import SQLiteWriter


def suggest_d3(type_):
    if type_ in ("IC50", "EC50"):
        return ".3e"
    elif type_.startswith("inh"):
        return ".1f"
    elif type_.startswith("raw"):
        return ".1f"
    elif type_.startswith("ratio"):
        return ".2f"
    elif type_.startswith("count"):
        return "d"
    elif type_.startswith("is"):
        return "d"
    elif type_ in ("valid", "flag"):
        return "d"


class ExperimentDataDemo(Workflow):
    def __init__(self):
        super().__init__()
        dest = "exp_results_demo.sqlite3"
        merge = MergeRecords()
        for in_file in glob.glob("./raw/exp_results_demo/*.txt"):
            csv_in = CSVFileReader(in_file, delimiter="\t")
            stack = Stack(["compoundID"])
            self.connect(csv_in, stack)
            self.connect(stack, merge)
        self.connect(merge, SplitField(
            "field", ("assay_id", "value_type"), ":",
            fields=[
                {"key": "assay_id", "name": "Assay ID", "format": "text"},
                {"key": "value_type", "name": "Value type", "format": "text"}
            ]
        ))
        self.append(Extend(
            "format", "value_type", func=suggest_d3,
            fields=[
                {"key": "format", "name": "Format", "format": "text"},
                {"key": "value", "name": "Value", "format": "numeric"}
            ],
            params={
                "sqlite_schema": {
                    "id": "exp_results",
                    "table": "RESULTS",
                    "name": "Experiment results",
                    "description": "Demo dataset",
                    "domain": "activity",
                    "resourceFile": dest
                }
            }
        ))
        self.append(UpdateFields(
            {"compoundID": "compound_id"}, fields=[static.COMPID_FIELD]))
        self.append(SQLiteWriter(
            os.path.join(conf.SQLITE_BASE_DIR, dest),
            create_index=("compound_id",)
        ))


if __name__ == '__main__':
    wf = ExperimentDataDemo()
    task = Task(wf)
    IOLoop.current().run_sync(task.execute)
    print("done")
