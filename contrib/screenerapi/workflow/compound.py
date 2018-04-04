#
# (C) 2014-2017 Seiji Matsuoka
# Licensed under the MIT License (MIT)
# http://opensource.org/licenses/MIT
#

import base64
import functools
import os

from flashflood.core.container import Container
from flashflood.core.workflow import Workflow
from flashflood.node.reader.httpfetch import HttpFetchInput
from flashflood.node.field.extend import Extend
from flashflood.node.field.number import Number
from flashflood.node.field.remove import RemoveField
from flashflood.node.field.update import UpdateFields
from flashflood.node.writer.container import ContainerWriter

from flashflood import static
from contrib.screenerapi import configparser as conf

"""
compounds?qcsRefIds=QCS001&layerIndices=1&q=q&fields=f&sort=s&offset=1&limit=50
"""


def queryString(query):
    ls = []
    for k, v in query.items():
        ls.append("{}={}".format(k, v))
    return "&".join(ls)


def elem(key, rcd):
    return rcd[key]


class Compound(Workflow):
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
        url = os.path.join(
            conf.BASE_URL, "compounds?{}".format(queryString(query)))
        self.append(HttpFetchInput(
            url, headers=self.headers,
            response_parser=lambda x: x["compounds"]
        ))
        """
        self.append(
            Fields("qcsRefId", "layerIndex", "compoundId", "fitting")
        )
        """
        self.append(Extend(
            "qAC50Mode", "fitting",
            func=functools.partial(elem, "qAC50Mode")
        ))
        self.append(Extend(
            "value", "fitting",
            func=functools.partial(elem, "linearQAC50")
        ))
        self.append(Extend(
            "drcPlot", "fitting",
            func=functools.partial(elem, "drcPlot")
        ))
        self.append(
            RemoveField("fitting")
        )
        self.append(UpdateFields(
            {"compoundId": "compound_id"},
            fields=[
                static.COMPID_FIELD
            ]
        ))
        self.append(Number("index"))
        self.append(ContainerWriter(self.results))
