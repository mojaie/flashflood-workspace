
import time

from tornado import web

from ffws import handler
from contrib.kegg import parser
from contrib.kegg.workflow.findcompounds import KeggFindCompounds


class GetCompoundHandler(web.RequestHandler):
    def get(self, compoundid):
        rcdquery = f"http://rest.kegg.jp/get/{compoundid}"
        molquery = f"http://rest.kegg.jp/get/{compoundid}/mol"
        rcd = parser.rcdfetch(rcdquery, {})
        time.sleep(0.01)  # access interval
        rcd["__molobj"] = parser.molfetch(molquery, {}).jsonized()
        self.write(rcd)


class FindCompoundsHandler(handler.AsyncWorkflowHandler):
    def initialize(self, **kwargs):
        super().initialize(KeggFindCompounds, **kwargs)


def install(application, params, **kwargs):
    application.add_handlers(r".*", [
        (r"/kegg/compound/(.*)", GetCompoundHandler),
        (r"/kegg/findcompounds", FindCompoundsHandler, params)
    ])
