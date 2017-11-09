
import os

from chorus import molutil
from tornado.ioloop import IOLoop

from kiwiii import static
from kiwiii.core.workflow import Workflow
from kiwiii.node.function.molecule import Molecule
from kiwiii.node.field.update import UpdateFields
from kiwiii.node.io.sqlitewriter import SQLiteWriter
from kiwiii.node.io.sdfile import SDFileInput


class ChemLibDemo(Workflow):
    def __init__(self):
        super().__init__()
        self.params = {
            "domain": "chemical",
            "type": "sqlite",
            "file": "chem_data_demo.sqlite3",
            "description": "Default SQLite chemical database"
        }
        sdf_in = SDFileInput(
            "./raw/chem_data_demo/DrugBank_FDA_Approved.sdf",
            fields=["DRUGBANK_ID", "GENERIC_NAME"],
            params={
                "id": "drugbankfda", "table": "DRUGBANKFDA",
                "name": "DrugBank FDA Approved",
                "description": "Demo dataset"
            }
        )
        molecule = Molecule(
            fields=[
                {"key": "_molobj"},
                {"key": "_mw_wo_sw", "name": "MW w/o salt and water",
                 "valueType": "numeric"}
            ],
            chem_calcs={"_mw_wo_sw": molutil.mw_wo_sw},
            pickle_mol=True
        )
        update_fields = UpdateFields({
            "DRUGBANK_ID": {"key": "id", "name": "ID",
                            "valueType": "compound_id"},
            "GENERIC_NAME": {"key": "name", "name": "Name",
                             "valueType": "text"}
        })
        writer = SQLiteWriter(
            self, os.path.join(static.SQLITE_BASE_DIR, self.params["file"]))
        self.connect(sdf_in, molecule)
        self.connect(molecule, update_fields)
        self.connect(update_fields, writer)


if __name__ == '__main__':
    wf = ChemLibDemo()
    IOLoop.current().run_sync(wf.submit)
    print("done")
