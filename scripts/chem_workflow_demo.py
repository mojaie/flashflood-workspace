
from chorus import molutil
from tornado.ioloop import IOLoop

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
            "file": "./raw/chem_data_demo/DrugBank_FDA_Approved.sdf",
            "description": "Default SQLite chemical database"
        }
        e1, = self.add_node(SDFileInput(
            self.params["file"],
            fields=["DRUGBANK_ID", "GENERIC_NAME"],
            params={
                "id": "drugbankfda",
                "table": "DRUGBANKFDA",
                "name": "DrugBank FDA Approved",
                "description": "Demo dataset"
            }
        ))
        e2, = self.add_node(Molecule(
            e1, fields=[{
                "key": "_mw_wo_sw", "name": "MW w/o salt and water",
                "dataType": "numeric"}],
            chem_calcs={"_mw_wo_sw": molutil.mw_wo_sw}
        ))
        e3, = self.add_node(UpdateFields(e2, {
            "DRUGBANK_ID": {"key": "id", "name": "ID",
                            "dataType": "compound_id"},
            "GENERIC_NAME": {"key": "name", "name": "Name", "dataType": "text"}
        }))
        self.add_node(
            SQLiteWriter([e3], self, "./resources/chem_data_demo.sqlite3"))


if __name__ == '__main__':
    wf = ChemLibDemo()
    IOLoop.current().run_sync(wf.submit)
