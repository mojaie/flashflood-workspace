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

from contrib.screenerapi import configparser as conf


def queryString(query):
    ls = []
    for k, v in query.items():
        ls.append("{}={}".format(k, v))
    return "&".join(ls)


class Compound(Workflow):
    def __init__(self, query):
        super().__init__()
        self.query = query
        # TODO: process comma separated qcsRefIds
        qcsid = self.query["qcsRefIds"]
        self.name = f"{qcsid}: compounds"
        # TODO: login
        user = "guest"
        passwd = "pass"
        login = base64.b64encode(
            bytes(f"{user}:{passwd}", "utf-8")).decode("utf-8")
        self.headers = {"Authorization": f"Basic {login}"}
        self.results = Container()
        if "fields" not in query:
            query["fields"] = [
                "qcsRefId", "layerIndex", "compoundId",
                "fitting.linearQAC50", "fitting.qAC50Mode", "fitting.drcPlot"
            ]
        if "limit" not in query:
            query["limit"] = 500
        query["fields"] = "%2C".join(query["fields"])
        url = os.path.join(conf.BASE_URL, f"compounds?{queryString(query)}")
        self.append(nd.HttpFetchInput(
            url, headers=self.headers,
            response_parser=lambda x: json.loads(x)["compounds"]
        ))
        self.append(nd.Extract(
            "fitting",
            ["linearQAC50", "qAC50Mode", "drcPlot"],
            in_place=True)
        )
        self.append(nd.Extend("structure", "compoundId"))
        self.append(nd.UpdateFields(
            {
                "compoundId": "compound_id", "layerIndex": "layer_id",
                "linearQAC50": "ac50", "drcPlot": "drcplot",
                "qAC50Mode": "ac50mode"
            },
            fields=[
                static.COMPID_FIELD,
                {"key": "structure", "name": "Structure",
                 "format": "async_html", "request": "../req/compound/"},
                {"key": "ac50", "name": "AC50", "d3_format": ".3e"},
                {"key": "ac50mode", "name": "AC50 mode", "format": "text"},
                {"key": "layer_id", "name": "Layer", "format": "text"},
                {"key": "drcplot", "name": "Dose response",
                 "format": "async_image", "request": conf.BASE_URL}
            ]
        ))
        self.append(nd.Number("index"))
        self.append(nd.ContainerWriter(self.results))
