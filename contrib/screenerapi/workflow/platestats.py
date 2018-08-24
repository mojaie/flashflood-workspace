#
# (C) 2014-2017 Seiji Matsuoka
# Licensed under the MIT License (MIT)
# http://opensource.org/licenses/MIT
#

import base64
import json
import os

from flashflood.core.container import Container
from flashflood.core.workflow import Workflow
from flashflood.node.reader.httpfetch import HttpFetchInput
from flashflood.node.field.extract import Extract
from flashflood.node.field.number import Number
from flashflood.node.writer.container import ContainerWriter

from contrib.screenerapi import configparser as conf


def queryString(query):
    ls = []
    for k, v in query.items():
        ls.append("{}={}".format(k, v))
    return "&".join(ls)


class PlateStats(Workflow):
    def __init__(self, query):
        super().__init__()
        self.name = "ScreenerAPI:PlateStats"
        user = "guest"
        passwd = "pass"
        encoded = base64.b64encode(bytes(":".join([user, passwd]), "utf-8"))
        self.query = query
        self.headers = {
            "Authorization": "Basic {}".format(encoded.decode("utf-8"))
        }
        self.results = Container()
        self.data_type = "nodes"
        if "fields" not in query:
            query["fields"] = [
                "qcsRefId", "barcode", "layerIndex", "wellCount", "masked",
                "zPrime", "zPrimeRobust", "signalToBackground", "wellTypes"
            ]
        if "limit" not in query:
            query["limit"] = 500
        query["fields"] = "%2C".join(query["fields"])
        url = os.path.join(
            conf.BASE_URL, "plates?{}".format(queryString(query)))
        self.append(HttpFetchInput(
            url, headers=self.headers,
            response_parser=lambda x: json.loads(x)["plates"]
        ))
        self.append(Extract(
            "wellTypes",
            ["NEUTRAL_CONTROL", "INHIBITOR_CONTROL"],
            in_place=True)
        )
        self.append(Number("index"))

        self.append(ContainerWriter(self.results))
