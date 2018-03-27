
import glob
import os
import yaml

from tornado.ioloop import IOLoop

from flashflood import configparser as conf
from flashflood import static
from flashflood.lod import ListOfDict
from flashflood.core.task import Task
from flashflood.core.workflow import Workflow
from flashflood.node.field.constant import ConstantField
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
        schema = {
            "id": "exp_results",
            "name": "Experiment results",
            "domain": "activity",
            "description": "Demo dataset",
            "resourceFile": "exp_results_demo.sqlite3",
            "table": "RESULTS"
        }

        # TODO: Auto detection of value types 1
        with open("./raw/assay_description.yaml", "r") as f:
            desc = yaml.load(f)
        data = ListOfDict(desc[0]["data"])

        merge = MergeRecords()
        for in_file in glob.glob("./raw/exp_results_demo/*.txt"):
            csv_in = CSVFileReader(in_file, delimiter="\t")

            # TODO: Auto detection of value types 2
            for field in csv_in.fields:
                if field["key"] == "compoundID":
                    continue
                id_, vtype = field["key"].split(":")
                rcd = data.find("assay_id", id_)
                if rcd is None:
                    continue
                if "value_types" not in rcd:
                    rcd["value_types"] = ListOfDict()
                rcd["value_types"].add({
                    "key": vtype, "name": vtype, "d3_format": suggest_d3(vtype)
                })

            stack = Stack(["compoundID"])
            self.connect(csv_in, stack)
            self.connect(stack, merge)

        # TODO: Auto detection of value types 3
        desc[0]["data"] = list(data)
        for d in desc[0]["data"]:
            if "value_types" in d:
                d["value_types"] = list(d["value_types"])
        desc[0]["fields"].append({
            "key": "value_types", "name": "Value types", "format": "list"})
        with open("./resources/assay_description.yaml", "w") as f:
            yaml.dump(desc, f)

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
            params={"sqlite_schema": schema}
        ))
        self.append(UpdateFields(
            {"compoundID": "compound_id"}, fields=[static.COMPID_FIELD]))
        self.append(ConstantField(
            "__source", schema["id"],
            fields=[{"key": "__source", "name": "Source", "format": "text"}]
        ))
        self.append(SQLiteWriter(
            os.path.join(conf.SQLITE_BASE_DIR, schema["resourceFile"]),
            create_index=("compound_id",)
        ))


if __name__ == '__main__':
    wf = ExperimentDataDemo()
    task = Task(wf)
    IOLoop.current().run_sync(task.execute)
    print("done")
