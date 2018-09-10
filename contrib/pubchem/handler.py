

from ffws import handler
from contrib.pubchem.workflow.compound import Compound
from contrib.pubchem.workflow.assay import Assay


class CompoundHandler(handler.WorkflowHandler):
    def initialize(self):
        super().initialize(Compound)


class AssayHandler(handler.WorkflowHandler):
    def initialize(self):
        super().initialize(Assay)


def install(application):
    application.add_handlers(r".*", [
        (r"/pubchem/compound", CompoundHandler),
        (r"/pubchem/assay", AssayHandler)
    ])
