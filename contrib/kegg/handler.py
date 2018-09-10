
import time

from chorus import v2000reader
from chorus import molutil
from tornado import httpclient
from tornado import web

from contrib.kegg import parser


def rcdfetch(url, headers):
    http_client = httpclient.HTTPClient()
    request = httpclient.HTTPRequest(url)
    request.headers = headers
    try:
        res = http_client.fetch(request)
        rcd = parser.compound_record(res.body.decode("utf-8"))
    except httpclient.HTTPError:
        rcd = {}
    finally:
        http_client.close()
    return rcd


def molfetch(url, headers):
    http_client = httpclient.HTTPClient()
    request = httpclient.HTTPRequest(url)
    request.headers = headers
    try:
        res = http_client.fetch(request)
        try:
            rcd = v2000reader.mol_from_text(res.body.decode("utf-8"))
        except ValueError:
            rcd = molutil.null_molecule()
    except httpclient.HTTPError:
        rcd = molutil.null_molecule()
    finally:
        http_client.close()
    return rcd


class GetCompoundHandler(web.RequestHandler):
    def get(self, compoundid):
        rcdquery = f"http://rest.kegg.jp/get/{compoundid}"
        molquery = f"http://rest.kegg.jp/get/{compoundid}/mol"
        rcd = rcdfetch(rcdquery, {})
        time.sleep(0.01)  # access interval
        rcd["__molobj"] = molfetch(molquery, {}).jsonized()
        self.write(rcd)


def install(application):
    application.add_handlers(r".*", [
        (r"/kegg/compound/(.*)", GetCompoundHandler)
    ])
