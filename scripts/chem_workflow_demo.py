
import os

from tornado.ioloop import IOLoop

from flashflood import configparser as conf
from flashflood import static
from flashflood.core.workflow import Workflow
from flashflood.node.chem.descriptor import MolDescriptor
from flashflood.node.chem.molecule import PickleMolecule
from flashflood.node.field.update import UpdateFields
from flashflood.node.reader.sdfile import SDFileReader
from flashflood.node.writer.sqlite import SQLiteWriter


class ChemLibDemo(Workflow):
    def __init__(self):
        super().__init__()
        db_schema = {
            "domain": "chemical",
            "resourceType": "sqlite",
            "resourceFile": "chem_data_demo.sqlite3",
            "description": "Default SQLite chemical database"
        }
        self.append(SDFileReader(
            "./raw/chem_data_demo/DrugBank_FDA_Approved.sdf",
            sdf_options=["DRUGBANK_ID", "GENERIC_NAME"],
            params={
                "sqlite_table_schema": {
                    "id": "drugbankfda", "table": "DRUGBANKFDA",
                    "name": "DrugBank FDA Approved",
                    "description": "Demo dataset"
                }
            }
        ))
        self.append(MolDescriptor(["_mw_wo_sw"]))
        self.append(UpdateFields(
            {"DRUGBANK_ID": "compound_id", "GENERIC_NAME": "name"},
            fields=[static.COMPID_FIELD, static.NAME_FIELD]
        ))
        self.append(PickleMolecule())
        self.append(SQLiteWriter(
            os.path.join(conf.SQLITE_BASE_DIR, db_schema["resourceFile"]),
            create_index=("_mw_wo_sw",), db_schema=db_schema
        ))


if __name__ == '__main__':
    IOLoop.current().run_sync(ChemLibDemo().execute)
    print("done")
