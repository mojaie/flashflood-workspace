
import urllib

from tornado import httpclient


def fetch(url):
    http_client = httpclient.HTTPClient()
    request = httpclient.HTTPRequest(url)
    try:
        res = http_client.fetch(request)
        rcd = res.body.decode("utf-8")
    except httpclient.HTTPError:
        rcd = {}
    finally:
        http_client.close()
    return rcd


def fetch_post(url, queries):
    http_client = httpclient.HTTPClient()
    body = urllib.parse.urlencode(queries)
    request = httpclient.HTTPRequest(url)
    request.method = "POST"
    request.body = body
    request.headers = {"Content-Type": "application/x-www-form-urlencoded"}
    try:
        res = http_client.fetch(request)
        rcd = res.body.decode("utf-8")
    except httpclient.HTTPError:
        rcd = {}
    finally:
        http_client.close()
    return rcd
