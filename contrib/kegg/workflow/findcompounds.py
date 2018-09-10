#
# (C) 2014-2017 Seiji Matsuoka
# Licensed under the MIT License (MIT)
# http://opensource.org/licenses/MIT
#

from chorus import v2000reader
from chorus import molutil
from flashflood import static
from flashflood.core.container import Container
from flashflood.core.workflow import AsyncWorkflow
import flashflood.node as nd

from contrib.screenerapi import configparser as conf


def rcdparser(text):
    res = []
    for line in text.strip().split("\n"):
        res.append({"cid": line[4:10], "name": line[11:]})
    return res


def molparser(ctab):
    try:
        mol = v2000reader.mol_from_text(ctab)
    except ValueError:
        mol = molutil.null_molecule()
    return {"__molobj": mol}


def molfailed():
    return molutil.null_molecule()


class KeggFindCompound(AsyncWorkflow):
    def __init__(self, query):
        super().__init__()
        self.query = query
        q = "/" + query["query"]
        op = "/" + query["option"]
        rcdquery = f"http://rest.kegg.jp/find/compound{q}{op}"
        self.name = rcdquery
        self.results = Container()

        self.append(nd.HttpFetchInput(rcdquery, response_parser=parser))
        self.append(nd.AsyncHttpBatchRequest(
            "response", "query", response_parser=parser
        ))
        # TODO: AsyncExtract
        self.append(nd.Extract(
            "response",
            ["entry", "name", "pathway", "module", "enzyme", "__molobj"],
            in_place=True
        ))
        self.append(nd.Extract(
            "dblinks",
            ["CAS", "PubChem", "ChEBI", "ChEMBL"],
            in_place=True
        ))
        # Choose first one from synonyms
        # TODO: AsyncExtend
        self.append(nd.Extend(
            "name", "name", lambda x: x[0], in_place=True
        ))
        self.append(nd.AsyncMolDescriptor(static.MOL_DESC_KEYS))
        self.append(nd.AsyncMoleculeToJSON())
        # TODO: AsyncUpdateFields
        self.append(nd.UpdateFields(
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
                {"key": "drcplot", "name": "Dose response",
                 "format": "async_image", "request": conf.BASE_URL}
            ]
        ))
        self.append(nd.AsyncNumber("index"))
        self.append(nd.ContainerWriter(self.results))
