#
# (C) 2014-2018 Seiji Matsuoka
# Licensed under the MIT License (MIT)
# http://opensource.org/licenses/MIT
#

import base64
import json
import os

from flashflood.core.container import Container
from flashflood.core.workflow import Workflow
import flashflood.node as nd

from contrib.screenerapi import configparser as conf


def queryString(query):
    ls = []
    for k, v in query.items():
        ls.append("{}={}".format(k, v))
    return "&".join(ls)


class PlateStats(Workflow):
    def __init__(self, query):
        super().__init__()
        self.query = query
        # TODO: process comma separated qcsRefIds
        self.name = f"{self.query['qcsRefIds']}: plate stats"
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
                "zPrime", "zPrimeRobust", "signalToBackground", "wellTypes"
            ]
        if "limit" not in query:
            query["limit"] = 500
        query["fields"] = "%2C".join(query["fields"])
        url = os.path.join(
            conf.BASE_URL, "plates?{}".format(queryString(query)))
        self.append(nd.HttpFetchInput(
            url, headers=self.headers,
            response_parser=lambda x: json.loads(x)["plates"],
        ))
        self.append(nd.Extract(
            "wellTypes", ["NEUTRAL_CONTROL", "INHIBITOR_CONTROL"],
            in_place=True
        ))
        self.append(nd.Extract(
            "NEUTRAL_CONTROL", ["mean", "median", "sd", "rsd"], in_place=True
        ))
        npf = "Neutral control"
        self.append(nd.UpdateFields(
            {
                "mean": "n_mean", "median": "n_med",
                "sd": "n_sd", "rsd": "n_rsd"
            }
        ))
        self.append(nd.Extract(
            "INHIBITOR_CONTROL", ["mean", "median", "sd", "rsd"], in_place=True
        ))
        ipf = "Inhibitor control"
        self.append(nd.UpdateFields(
            {
                "mean": "i_mean", "median": "i_med",
                "sd": "i_sd", "rsd": "i_rsd"
            }
        ))
        self.append(nd.UpdateFields(
            {
                "barcode": "plate_id", "layerIndex": "layer_id",
                "signalToBackground": "sb_ratio",
                "zPrime": "z_prime", "zPrimeRobust": "rz_prime"
            },
            fields=[
                {"key": "plate_id", "name": "Plate ID", "format": "text"},
                {"key": "layer_id", "name": "Layer", "format": "text"},
                {"key": "sb_ratio", "name": "S/B", "d3_format": ".2f"},
                {"key": "z_prime", "name": "Z'", "d3_format": ".3f"},
                {"key": "rz_prime", "name": "RZ'", "d3_format": ".3f"},
                {"key": "n_mean", "name": f"{npf} mean", "d3_format": "~f"},
                {"key": "n_med", "name": f"{npf} median", "d3_format": "~f"},
                {"key": "n_sd", "name": f"{npf} SD", "d3_format": "~f"},
                {"key": "n_rsd", "name": f"{npf} RSD", "d3_format": "~f"},
                {"key": "i_mean", "name": f"{ipf} mean", "d3_format": "~f"},
                {"key": "i_med", "name": f"{ipf} median", "d3_format": "~f"},
                {"key": "i_sd", "name": f"{ipf} SD", "d3_format": "~f"},
                {"key": "i_rsd", "name": f"{ipf} RSD", "d3_format": "~f"}
            ]
        ))
        self.append(nd.Number("index"))

        self.append(nd.ContainerWriter(self.results))
