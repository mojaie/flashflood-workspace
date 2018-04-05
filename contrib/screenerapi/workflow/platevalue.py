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
from flashflood.node.transform.unstack import Unstack
from flashflood.node.writer.container import ContainerWriter

from contrib.screenerapi import configparser as conf


def queryString(query):
    ls = []
    for k, v in query.items():
        ls.append("{}={}".format(k, v))
    return "&".join(ls)


class PlateValue(Workflow):
    def __init__(self, query):
        super().__init__()
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
                "wells.types", "wells.rawValues", "wells.compoundIds",
                "wells.masked"
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
            "wells",
            ["rawValues", "compoundIds", "types", "masked"],
            in_place=True)
        )
        self.append(Unstack(
            ["barcode"], "layerIndex", "rawValues", label_prefix="layer-"))
        self.append(Number("index"))

        self.append(ContainerWriter(self.results))
