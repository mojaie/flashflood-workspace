#
# (C) 2014-2017 Seiji Matsuoka
# Licensed under the MIT License (MIT)
# http://opensource.org/licenses/MIT
#

import functools
import traceback

from chorus import rdkit
from flashflood import static
from flashflood.core.concurrent import ConcurrentFilter
from flashflood.core.container import Container, Counter
from flashflood.core.workflow import Workflow
import flashflood.node as nd

from ffws import sqlite


def rdfmcs_calc(qmol, timeout, row):
    try:
        res = rdkit.fmcs(row["__molobj"], qmol, timeout=timeout)
    except:
        print(traceback.format_exc())
        return
    row["fmcs_sim"] = res["similarity"]
    row["fmcs_edges"] = res["mcs_edges"]
    return row


def thld_filter(thld, measure, row):
    if row is None:
        return
    type_ = {"sim": "fmcs_sim", "edge": "fmcs_edges"}
    return row[type_[measure]] >= thld


class RDKitFMCS(Workflow):
    def __init__(self, query, **kwargs):
        super().__init__(**kwargs)
        self.query = query
        measure = query["params"]["measure"]
        thld = float(query["params"]["threshold"])
        timeout = int(query["params"]["timeout"])
        molquerystr = {
            "molfile": "SDFile",
            "dbid": "{}{}".format(
                query["queryMol"]["source"], query["queryMol"]["value"])
        }
        measurestr = {"sim": "FMCSJaccard", "edges": "FMCSedges"}
        self.name = "{}>={}_{}".format(
            measurestr[measure], thld,
            molquerystr[query["queryMol"]["format"]])
        self.results = Container()
        self.done_count = Counter()
        self.input_size = Counter()
        self.append(nd.SQLiteReader(
            [sqlite.find_resource(t) for t in query["targets"]],
            fields=sqlite.merged_fields(query["targets"]),
            counter=self.input_size
        ))
        self.append(nd.UnpickleMolecule())
        qmol = sqlite.query_mol(query["queryMol"])
        self.append(ConcurrentFilter(
            functools.partial(thld_filter, thld, measure),
            func=functools.partial(rdfmcs_calc, qmol, timeout),
            residue_counter=self.done_count,
            fields=[
                {"key": "fmcs_sim", "name": "MCS similarity",
                 "d3_format": ".2f"},
                {"key": "fmcs_edges", "name": "MCS size", "d3_format": "d"}
            ]
        ))
        self.append(nd.AsyncMolDescriptor(static.MOL_DESC_KEYS))
        self.append(nd.AsyncMoleculeToJSON())
        self.append(nd.AsyncNumber("index", fields=[static.INDEX_FIELD]))
        self.append(nd.AsyncCountRows(self.done_count))
        self.append(nd.ContainerWriter(self.results))
