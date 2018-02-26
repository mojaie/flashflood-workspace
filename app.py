
import time

from tornado import web
from tornado.ioloop import IOLoop
from tornado.options import define, options, parse_command_line

from flashflood import configparser as conf
from flashflood.core.jobqueue import JobQueue
from flashflood.handler import handler


def run():
    define("port", default=8888, help="run on the given port", type=int)
    define("debug", default=False, help="run in debug mode")
    parse_command_line()
    instance_prefix = conf.INSTANCE_PREFIX
    timestamp = time.strftime("%X %x %Z", time.localtime(time.time()))
    params = {
        "jobqueue": JobQueue(),
        "instance": "".join((instance_prefix, timestamp))
    }
    wpath = {True: conf.WEB_BUILD, False: conf.WEB_DIST}[options.debug]
    handlers = [
        (r"/search", handler.ChemDBSearch),
        (r"/filter", handler.ChemDBFilter, params),
        (r"/profile", handler.Profile),
        (r"/exact", handler.ExactStruct),
        (r"/substr", handler.Substruct, params),
        (r"/supstr", handler.Superstruct, params),
        (r"/gls", handler.GLS, params),
        (r"/rdmorgan", handler.RDKitMorgan, params),
        (r"/rdfmcs", handler.RDKitFMCS, params),
        (r"/glsnet", handler.GLSNetwork, params),
        (r"/rdmorgannet", handler.RDKitMorganNetwork, params),
        (r"/rdfmcsnet", handler.RDKitFMCSNetwork, params),
        (r"/progress", handler.WorkflowProgress, params),
        (r"/strprev", handler.StructurePreview),
        (r"/sdfin", handler.SDFileParser),
        (r"/sdfout", handler.SDFileExport),
        (r"/xlsx", handler.ExcelExport),
        (r"/schema", handler.Schema),
        (r"/server", handler.ServerStatus, params),
        (r"/(.*)", web.StaticFileHandler, {"path": wpath})
    ]
    hs = [("".join([conf.URL_PREFIX, h[0]]), *h[1:]) for h in handlers]
    settings = dict(
        debug=options.debug,
        compress_response=True,
        cookie_secret="_TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE_"
    )
    app = web.Application(hs, **settings)
    app.listen(options.port)
    try:
        print("Server started")
        IOLoop.current().start()
    except KeyboardInterrupt:
        print("Server stopped")


if __name__ == "__main__":
    run()
