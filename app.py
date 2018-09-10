
import importlib
from pathlib import Path
import time

from tornado import web
from tornado.ioloop import IOLoop
from tornado.options import define, options, parse_command_line
from flashflood.core.jobqueue import JobQueue

from ffws import configparser as conf
from ffws import handler


def run():
    define("port", default=8888, help="run on the given port", type=int)
    define("debug", default=False, help="run in debug mode")
    parse_command_line()

    # Remove temporary job results
    if list(Path(conf.TEMP_DIR).glob("*.json.gz")):
        res = input(
            "Job result caches are found. Do you want to clear them ? (y): ")
        if res.lower() == "y":
            for p in Path(conf.TEMP_DIR).glob("*.json.gz"):
                p.unlink()
            print("Job result caches are deleted.")

    timestamp = time.strftime("%X %x %Z", time.localtime(time.time()))
    params = {
        "jobqueue": JobQueue(),
        "instance": f"{conf.INSTANCE_PREFIX}{timestamp}"
    }
    handlers = [
        (r"/search", handler.ChemDBSearch),
        (r"/filter", handler.ChemDBFilter, params),
        (r"/profile", handler.Profile),
        (r"/activity", handler.Activity),
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
        (r"/compound/(.*)", handler.StructureByID),
        (r"/strprev", handler.StructurePreview),
        (r"/sdfin", handler.SDFileParser),
        (r"/sdfout", handler.SDFileExport),
        (r"/xlsx", handler.ExcelExport),
        (r"/schema", handler.Schema),
        (r"/server", handler.ServerStatus, params)
    ]
    hs = [(f"/{conf.API_URL_PREFIX}{h[0]}", *h[1:]) for h in handlers]
    hs.append((
        f"/{conf.APP_BUNDLE_URL_PREFIX}/(.*)", web.StaticFileHandler,
        {"path": {
                True: conf.WEB_DEBUG_BUILD_DIR,
                False: conf.WEB_BUILD_DIR
            }[options.debug]
         }
    ))
    hs.append((
        f"/{conf.ASSETS_URL_PREFIX}/(.*)", web.StaticFileHandler,
        {"path": conf.WEB_ASSETS_DIR}
    ))
    hs.append((
        r"/(sw.js)", web.StaticFileHandler,
        {"path": "node_modules/kiwiii/docs/"}
    ))
    settings = dict(
        debug=options.debug,
        compress_response=True,
        cookie_secret="_TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE_"
    )
    app = web.Application(hs, **settings)

    for ext in conf.EXTERNALS:
        mod = ext["module"]
        importlib.import_module(f"{mod}.handler").install(app, params=params)

    app.listen(options.port)
    try:
        print("Server started")
        IOLoop.current().start()
    except KeyboardInterrupt:
        print("Server stopped")


if __name__ == "__main__":
    run()
