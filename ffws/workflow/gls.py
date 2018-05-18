#
# (C) 2014-2017 Seiji Matsuoka
# Licensed under the MIT License (MIT)
# http://opensource.org/licenses/MIT
#

import functools

from chorus import mcsdr
from chorus import molutil
from flashflood import static
from flashflood.core.concurrent import ConcurrentFilter
from flashflood.core.container import Container, Counter
from flashflood.core.node import FuncNode
from flashflood.core.workflow import Workflow
import flashflood.node as nd

from ffws import sqlite


def gls_array(ignoreHs, diam, tree, rcd):
    if rcd is None:
        return
    if ignoreHs:
        mol = molutil.make_Hs_implicit(rcd["__molobj"])
    else:
        mol = rcd["__molobj"]
    try:
        arr = mcsdr.comparison_array(mol, diam, tree)
    except ValueError:
        return
    else:
        rcd["array"] = arr
    return rcd


def gls_prefilter(thld, measure, qarr, rcd):
    if rcd is None:
        return
    sm, bg = sorted((qarr[1], rcd["array"][1]))
    if measure == "sim":
        if sm < bg * thld:
            return
    elif measure == "edge":
        if sm < thld:
            return
    return rcd


def gls_calc(qarr, timeout, rcd):
    if rcd is None:
        return
    res = mcsdr.from_array(qarr, rcd["array"], timeout)
    rcd["local_sim"] = res.local_sim()
    rcd["mcsdr"] = res.edge_count()
    del rcd["array"]
    return rcd


def thld_filter(thld, measure, rcd):
    if rcd is None:
        return False
    type_ = {"sim": "local_sim", "edge": "mcsdr"}
    return rcd[type_[measure]] >= thld


class GLS(Workflow):
    def __init__(self, query, **kwargs):
        super().__init__(**kwargs)
        self.query = query
        self.results = Container()
        self.done_count = Counter()
        self.input_size = Counter()
        self.data_type = "nodes"
        measure = query["params"]["measure"]
        ignoreHs = query["params"]["ignoreHs"]
        thld = float(query["params"]["threshold"])
        diam = int(query["params"]["diameter"])
        tree = int(query["params"]["maxTreeSize"])
        timeout = float(query["params"]["timeout"])
        qmol = sqlite.query_mol(query["queryMol"])
        qarr = mcsdr.comparison_array(qmol, diam, tree)
        self.append(nd.SQLiteReader(
            [sqlite.find_resource(t) for t in query["targets"]],
            fields=sqlite.merged_fields(query["targets"]),
            counter=self.input_size
        ))
        self.append(nd.UnpickleMolecule())
        self.append(FuncNode(
            functools.partial(gls_array, ignoreHs, diam, tree)))
        self.append(FuncNode(
            functools.partial(gls_prefilter, thld, measure, qarr)))
        self.append(ConcurrentFilter(
            functools.partial(thld_filter, thld, measure),
            func=functools.partial(gls_calc, qarr, timeout),
            residue_counter=self.done_count,
            fields=[
                {"key": "mcsdr", "name": "MCS-DR size", "d3_format": "d"},
                {"key": "local_sim", "name": "GLS", "d3_format": ".2f"}
            ]
        ))
        self.append(nd.AsyncMolDescriptor(static.MOL_DESC_KEYS))
        self.append(nd.AsyncMoleculeToJSON())
        self.append(nd.AsyncNumber("index", fields=[static.INDEX_FIELD]))
        self.append(nd.AsyncCountRows(self.done_count))
        self.append(nd.ContainerWriter(self.results))
