#
# (C) 2014-2018 Seiji Matsuoka
# Licensed under the MIT License (MIT)
# http://opensource.org/licenses/MIT
#

import time

from chorus import molutil
from flashflood import static
from flashflood.core.container import Container
from flashflood.core.workflow import Workflow
import flashflood.node as nd

from contrib.kegg import parser


def rcdparser(text):
    res = []
    for line in text.strip().split("\n"):
        res.append({
            "query": f"kegg/findcompounds/{line[4:10]}"
        })
    return res


def request(compoundid):
    rcdquery = f"http://rest.kegg.jp/get/{compoundid}"
    molquery = f"http://rest.kegg.jp/get/{compoundid}/mol"
    rcd = parser.rcdfetch(rcdquery, {})
    time.sleep(0.01)  # access interval
    rcd["__molobj"] = parser.molfetch(molquery, {})
    time.sleep(0.01)  # access interval
    return rcd


def molfailed():
    return molutil.null_molecule()


class KeggFindCompounds(Workflow):
    def __init__(self, query):
        super().__init__()
        self.query = query
        q = "/" + query["query"]
        op = "/" + query["option"]
        rcdquery = f"http://rest.kegg.jp/find/compound{q}{op}"
        self.name = rcdquery
        self.results = Container()

        self.append(nd.HttpFetchInput(rcdquery, response_parser=rcdparser))
        # self.append(nd.AsyncStdoutMonitor('kf', interval=1))
        self.append(nd.AsyncExtend(
            "response", "query", func=request, in_place=True
        ))
        self.append(nd.AsyncExtract(
            "response",
            ["entry", "name", "pathway", "module", "enzyme", "__molobj"],
            in_place=True
        ))
        """
        self.append(nd.AsyncExtract(
            "dblinks",
            ["CAS", "PubChem", "ChEBI", "ChEMBL"],
            in_place=True
        ))
        # Choose first one from synonyms
        self.append(nd.AsyncExtend(
            "name", "name", lambda x: x[0], in_place=True
        ))
        """
        self.append(nd.AsyncMolDescriptor(static.MOL_DESC_KEYS))
        self.append(nd.AsyncMoleculeToJSON())
        """
        self.append(nd.AsyncUpdateFields(
            {
                "entry": "compound_id", "layerIndex": "layer_id",
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
                {"key": "drcplot", "name": "Dose response"}
            ]
        ))
        """
        self.append(nd.AsyncNumber("index"))
        self.append(nd.ContainerWriter(self.results))
