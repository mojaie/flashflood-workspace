
import yaml

from kiwiii.core.workflow import Workflow
from kiwiii.node.function.molecule import Molecule
from kiwiii.node.field.update import UpdateFields
from kiwiii.node.io.sqlitewriter import SQLiteWriter
from kiwiii.node.io.sdfile import SDFileInput


class TextDemo(Workflow):
    def __init__(self):
        super().__init__()
        es = []
        for p in glob:
            specs = yaml.loads("./raw/text_demo/{}.yaml".format(p))
            e1, = self.add_node(CSVInput("./raw/text_demo/{}.txt".format(p)))
            e2, = self.add_node(UpdateFields(e1, {
                "DRUGBANK_ID": {"key": "id", "name": "ID",
                                "dataType": "compound_id"},
                "GENERIC_NAME": {"key": "name", "name": "Name", "dataType": "text"}
            }))
            es.append(e2)
        self.add_node(SQLiteWriter(es, self, "./resources/sdf_demo.sqlite3"))
