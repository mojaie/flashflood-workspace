

from ffws import handler
from contrib.screenerapi.workflow.compound import Compound
from contrib.screenerapi.workflow.platestats import PlateStats
from contrib.screenerapi.workflow.platevalue import PlateValue
from contrib.screenerapi.workflow.qcsession import QcSession


class CompoundHandler(handler.WorkflowHandler):
    def initialize(self):
        super().initialize(Compound)


class PlateValueHandler(handler.WorkflowHandler):
    def initialize(self):
        super().initialize(PlateValue)


class PlateStatsHandler(handler.WorkflowHandler):
    def initialize(self):
        super().initialize(PlateStats)


class QcSessionHandler(handler.WorkflowHandler):
    def initialize(self):
        super().initialize(QcSession)


def install(application):
    application.add_handlers(r".*", [
        (r"/screener/compound", CompoundHandler),
        (r"/screener/platevalue", PlateValueHandler),
        (r"/screener/platestats", PlateStatsHandler),
        (r"/screener/qcsession", QcSessionHandler)
    ])
