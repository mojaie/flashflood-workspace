
import os

from tornado.ioloop import IOLoop

from ffws import configparser as conf
from flashflood import static
from flashflood.core.task import Task
from flashflood.core.workflow import Workflow
import flashflood.node as nd


class ChemLibDemo(Workflow):
    def __init__(self):
        super().__init__()
        schema = {
            "id": "drugbankfda",
            "name": "DrugBank FDA Approved",
            "domain": "chemical",
            "description": "Demo dataset",
            "resourceFile": "chem_data_demo.sqlite3",
            "table": "DRUGBANKFDA"
        }
        self.append(nd.SDFileReader(
            "./raw/chem_data_demo/DrugBank_FDA_Approved.sdf",
            sdf_options=["DRUGBANK_ID", "GENERIC_NAME"],
            params={"sqlite_schema": schema}
        ))
        self.append(nd.MolDescriptor(["_mw_wo_sw"]))
        self.append(nd.UpdateFields(
            {"DRUGBANK_ID": "compound_id", "GENERIC_NAME": "name"},
            fields=[static.COMPID_FIELD, static.NAME_FIELD]
        ))
        self.append(nd.ConstantField(
            "__source", schema["id"],
            fields=[{"key": "__source", "name": "Source", "format": "text"}]
        ))
        self.append(nd.PickleMolecule())
        self.append(nd.SQLiteWriter(
            os.path.join(conf.SQLITE_BASE_DIR, schema["resourceFile"]),
            primary_key="compound_id", create_index=("_mw_wo_sw",)
        ))


if __name__ == '__main__':
    wf = ChemLibDemo()
    task = Task(wf)
    IOLoop.current().run_sync(task.execute)
    print("done")
