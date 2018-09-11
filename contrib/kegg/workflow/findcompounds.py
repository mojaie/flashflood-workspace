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
        res.append({"query": line[4:10]})
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
        # self.append(nd.AsyncStdoutMonitor("wf", interval=1))
        self.append(nd.AsyncExtend(
            "response", "query", func=request, in_place=True
        ))
        self.append(nd.AsyncExtract(
            "response",
            ["entry", "name", "pathway", "module", "enzyme", "dblinks",
             "__molobj"],
            in_place=True
        ))
        self.append(nd.AsyncExtract(
            "dblinks",
            ["CAS", "PubChem", "ChEBI", "ChEMBL"],
            in_place=True
        ))
        # Choose first one from synonyms
        self.append(nd.AsyncExtend(
            "name", "name", lambda x: x[0], in_place=True
        ))
        self.append(nd.AsyncUpdateFields(
            {"entry": "compound_id"},
            fields=[
                static.COMPID_FIELD,
                {"key": "_cas", "name": "CAS", "format": "text"},
                {"key": "_chebi", "name": "ChEBI", "format": "text"},
                {"key": "_chembl", "name": "ChEMBL", "format": "text"},
                {"key": "pubchem", "name": "PubChem", "format": "text"}
            ]
        ))
        self.append(nd.AsyncMolDescriptor(static.MOL_DESC_KEYS))
        self.append(nd.AsyncMoleculeToJSON())
        self.append(nd.AsyncNumber("index"))
        self.append(nd.ContainerWriter(self.results))
