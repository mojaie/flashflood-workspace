#
# (C) 2014-2017 Seiji Matsuoka
# Licensed under the MIT License (MIT)
# http://opensource.org/licenses/MIT
#

import base64
import json
import os

from flashflood import static
from flashflood.core.container import Container
from flashflood.core.workflow import Workflow
import flashflood.node as nd
from tornado import httpclient

from contrib.screenerapi import configparser as conf


def queryString(query):
    ls = []
    for k, v in query.items():
        ls.append("{}={}".format(k, v))
    return "&".join(ls)


class PlateValue(Workflow):
    def __init__(self, query):
        super().__init__()
        self.query = query
        # TODO: process comma separated qcsRefIds
        qcsid = self.query["qcsRefIds"]
        self.name = f"{qcsid}: plate values"
        # TODO: login
        user = "guest"
        passwd = "pass"
        login = base64.b64encode(
            bytes(f"{user}:{passwd}", "utf-8")).decode("utf-8")
        self.headers = {"Authorization": f"Basic {login}"}
        self.results = Container()
        if "fields" not in query:
            query["fields"] = [
                "qcsRefId", "barcode", "layerIndex", "wellCount", "masked",
                "wells.types", "wells.rawValues", "wells.compoundIds",
                "wells.masked"
            ]
        if "limit" not in query:
            query["limit"] = 500
        query["fields"] = "%2C".join(query["fields"])

        # Fetch QCS layer info
        lurl = os.path.join(conf.BASE_URL, f"qcSessions/{qcsid}?fields=layers")
        http_client = httpclient.HTTPClient()
        request = httpclient.HTTPRequest(lurl)
        request.headers = self.headers
        response = http_client.fetch(request)
        http_client.close()
        resjson = json.loads(response.body.decode("utf-8"))
        layerInfo = resjson["qcSessions"][0]["layers"]

        url = os.path.join(
            conf.BASE_URL, "plates?{}".format(queryString(query)))
        self.append(nd.HttpFetchInput(
            url, headers=self.headers,
            response_parser=lambda x: json.loads(x)["plates"]
        ))
        self.append(nd.Extract(
            "wells",
            ["rawValues", "compoundIds", "types", "masked"],
            in_place=True)
        )
        self.append(nd.Unstack(
            ["barcode"], "layerIndex", "rawValues", label_prefix="layer"
        ))
        self.append(nd.Zip(
            ["barcode"],
            [
                "compoundIds", "masked", "types",
                *[f"layer{layer['layerIndex']}" for layer in layerInfo]
            ]
        ))
        self.append(nd.UpdateFields(
            {
                "compoundIds": "compound_id", "barcode": "plate_id",
                "types": "type"
            },
            fields=[
                static.COMPID_FIELD,
                {"key": "plate_id", "name": "Plate ID", "format": "text"},
                {"key": "masked", "name": "Masked", "d3_format": "d"},
                {"key": "type", "name": "Well type", "format": "text"},
                *[{"key": f"layer{layer['layerIndex']}", "name": layer["name"],
                   "format": "text"} for layer in layerInfo]
            ]
        ))
        self.append(nd.Number("index"))

        self.append(nd.ContainerWriter(self.results))
