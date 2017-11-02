
from kiwiii.core.workflow import Workflow
from kiwiii.node.function.molecule import Molecule
from kiwiii.node.field.update import UpdateFields
from kiwiii.node.io.sqlitewriter import SQLiteWriter
from kiwiii.node.io.sdfile import SDFileInput


class SDFDemo(Workflow):
    def __init__(self):
        super().__init__
        self.id = "drugbankfda"
        self.name = "DrugBank FDA Approved(Demo)"
        self.table = "DRUGBANKFDA"
        e1, = self.add_node(SDFileInput(
            "./raw/sdf_demo/DrugBank_FDA_Approved.sdf",
            params={"fields": ["DRUGBANK_ID", "GENERIC_NAME"]}
        ))
        e2, = self.add_node(Molecule(e1, calc=["_mw_wo_sw"]))
        e3, = self.add_node(UpdateFields(e2, {
            "DRUGBANK_ID": {"key": "id", "name": "ID",
                            "dataType": "compound_id"},
            "GENERIC_NAME": {"key": "name", "name": "Name", "dataType": "text"}
        }))
        self.add_node(SQLiteWriter([e3], self, "./resources/sdf_demo.sqlite3"))
