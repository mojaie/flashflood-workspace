#
# (C) 2014-2017 Seiji Matsuoka
# Licensed under the MIT License (MIT)
# http://opensource.org/licenses/MIT
#

import functools

from chorus import mcsdr
from flashflood import static
from flashflood.core.concurrent import ConcurrentFilter
from flashflood.core.container import Container, Counter
from flashflood.core.workflow import Workflow
import flashflood.node as nd

from ffws import sqlite


def gls_calc(qarr, thld, diam, ignoreHs, timeout, rcd):
    arr = mcsdr.DescriptorArray(
        rcd["__molobj"], diameter=diam, ignore_hydrogen=ignoreHs)
    res = mcsdr.from_array(qarr, arr, timeout=timeout, gls_cutoff=thld)
    rcd["local_sim"] = res.local_sim()
    rcd["mcsdr"] = res.edge_count()
    return rcd


def mcsdr_calc(qarr, thld, diam, ignoreHs, timeout, rcd):
    arr = mcsdr.DescriptorArray(
        rcd["__molobj"], diameter=diam, ignore_hydrogen=ignoreHs)
    res = mcsdr.from_array(qarr, arr, timeout=timeout, edge_cutoff=thld)
    rcd["local_sim"] = res.local_sim()
    rcd["mcsdr"] = res.edge_count()
    return rcd


def gls_filter(thld, rcd):
    if rcd is None:
        return False
    return rcd["local_sim"] >= thld


def mcsdr_filter(thld, rcd):
    if rcd is None:
        return False
    return rcd["mcsdr"] >= thld


class GLS(Workflow):
    def __init__(self, query, **kwargs):
        super().__init__(**kwargs)
        self.query = query
        self.results = Container()
        self.done_count = Counter()
        self.input_size = Counter()
        measure = query["params"]["measure"]
        calc_func = {"sim": gls_calc, "edge": mcsdr_calc}[measure]
        filter_func = {"sim": gls_filter, "edge": mcsdr_filter}[measure]
        ignoreHs = query["params"]["ignoreHs"]
        thld = float(query["params"]["threshold"])
        diam = int(query["params"]["diameter"])
        timeout = float(query["params"]["timeout"])
        qmol = sqlite.query_mol(query["queryMol"])
        qarr = mcsdr.DescriptorArray(
            qmol, diameter=diam, ignore_hydrogen=ignoreHs)
        self.append(nd.SQLiteReader(
            [sqlite.find_resource(t) for t in query["targets"]],
            fields=sqlite.merged_fields(query["targets"]),
            counter=self.input_size
        ))
        self.append(nd.UnpickleMolecule())
        self.append(ConcurrentFilter(
            functools.partial(filter_func, thld),
            func=functools.partial(
                calc_func, qarr, thld, diam, ignoreHs, timeout),
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
