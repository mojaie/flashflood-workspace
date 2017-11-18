
import os

from chorus import molutil
from tornado.ioloop import IOLoop

from flashflood import configparser as conf
from flashflood import static
from flashflood.core.workflow import Workflow
from flashflood.node.chem.molecule import Molecule
from flashflood.node.field.update import UpdateFields
from flashflood.node.io.sqlitewriter import SQLiteWriter
from flashflood.node.io.sdfile import SDFileInput


class ChemLibDemo(Workflow):
    def __init__(self):
        super().__init__()
        self.params = {
            "domain": "chemical",
            "resourceType": "sqlite",
            "resourceFile": "chem_data_demo.sqlite3",
            "description": "Default SQLite chemical database"
        }
        sdf_in = SDFileInput(
            "./raw/chem_data_demo/DrugBank_FDA_Approved.sdf",
            sdf_options=["DRUGBANK_ID", "GENERIC_NAME"],
            params={
                "id": "drugbankfda", "table": "DRUGBANKFDA",
                "name": "DrugBank FDA Approved",
                "description": "Demo dataset"
            }
        )
        molecule = Molecule(
            chem_calcs={"_mw_wo_sw": molutil.mw_wo_sw},
            pickle_mol=True,
            fields=[
                {"key": "_molobj", "name": "Molecule object",
                 "valueType": "json"},
                {"key": "_mw_wo_sw", "name": "MW w/o salt and water",
                 "valueType": "numeric"}
            ]
        )
        update_fields = UpdateFields(
            {"DRUGBANK_ID": "compound_id", "GENERIC_NAME": "name"},
            fields=[static.COMPID_FIELD, static.NAME_FIELD]
        )
        writer = SQLiteWriter(
            self,
            os.path.join(conf.SQLITE_BASE_DIR, self.params["resourceFile"]),
            create_index=("_mw_wo_sw",)
        )
        self.connect(sdf_in, molecule)
        self.connect(molecule, update_fields)
        self.connect(update_fields, writer)


if __name__ == '__main__':
    wf = ChemLibDemo()
    IOLoop.current().run_sync(wf.submit)
    print("done")
