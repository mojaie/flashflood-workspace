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
from flashflood.node.field.update import UpdateFields
from flashflood.node.writer.container import ContainerWriter

from flashflood import static
from contrib.screenerapi import configparser as conf


def queryString(query):
    ls = []
    for k, v in query.items():
        ls.append("{}={}".format(k, v))
    return "&".join(ls)


class Compound(Workflow):
    def __init__(self, query):
        super().__init__()
        self.name = "ScreenerAPI:Compound"
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
                "qcsRefId", "layerIndex", "compoundId",
                "fitting.linearQAC50", "fitting.qAC50Mode", "fitting.drcPlot"
            ]
        if "limit" not in query:
            query["limit"] = 500
        query["fields"] = "%2C".join(query["fields"])
        url = os.path.join(
            conf.BASE_URL, "compounds?{}".format(queryString(query)))
        self.append(HttpFetchInput(
            url, headers=self.headers,
            response_parser=lambda x: json.loads(x)["compounds"]
        ))
        self.append(Extract(
            "fitting",
            ["linearQAC50", "qAC50Mode", "drcPlot"],
            in_place=True)
        )
        self.append(UpdateFields(
            {
                "compoundId": "compound_id",
                "linearQAC50": "value",
            },
            fields=[static.COMPID_FIELD]
        ))
        self.append(Number("index"))
        self.append(ContainerWriter(self.results))
