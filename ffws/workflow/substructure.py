#
# (C) 2014-2017 Seiji Matsuoka
# Licensed under the MIT License (MIT)
# http://opensource.org/licenses/MIT
#

import functools

from chorus import substructure
from chorus import molutil

from flashflood import static
from flashflood.core.concurrent import ConcurrentFilter
from flashflood.core.container import Container, Counter
from flashflood.core.workflow import Workflow
import flashflood.node as nd

from ffws import sqlite


def exact_filter(qmol, params, row):
    return substructure.equal(
            row["__molobj"], qmol, ignore_hydrogen=params["ignoreHs"])


def substr_filter(qmol, params, row):
    return substructure.substructure(
            row["__molobj"], qmol, ignore_hydrogen=params["ignoreHs"])


def supstr_filter(qmol, params, row):
    return substructure.substructure(
            qmol, row["__molobj"], ignore_hydrogen=params["ignoreHs"])


class ExactStruct(Workflow):
    def __init__(self, query, **kwargs):
        super().__init__(**kwargs)
        self.query = query
        molquerystr = {
            "molfile": "SDFile",
            "dbid": "{}{}".format(
                query["queryMol"]["source"], query["queryMol"]["value"])
        }
        self.name = "ExactMatch_{}".format(
            molquerystr[query["queryMol"]["format"]])
        self.results = Container()
        self.done_count = Counter()
        self.input_size = Counter()
        qmol = sqlite.query_mol(query["queryMol"])
        pred = functools.partial(exact_filter, qmol, query["params"])
        self.append(nd.SQLiteReaderFilter(
            [sqlite.find_resource(t) for t in query["targets"]],
            "_mw_wo_sw", molutil.mw(qmol), "=",
            fields=sqlite.merged_fields(query["targets"])
        ))
        self.append(nd.CountRows(self.input_size))
        self.append(nd.UnpickleMolecule())
        self.append(nd.Filter(pred, residue_counter=self.done_count))
        self.append(nd.MolDescriptor(static.MOL_DESC_KEYS))
        self.append(nd.MoleculeToJSON())
        self.append(nd.Number("index", fields=[static.INDEX_FIELD]))
        self.append(nd.CountRows(self.done_count))
        self.append(nd.ContainerWriter(self.results))


class Substruct(Workflow):
    def __init__(self, query, **kwargs):
        super().__init__(**kwargs)
        self.query = query
        molquerystr = {
            "molfile": "SDFile",
            "dbid": "{}{}".format(
                query["queryMol"]["source"], query["queryMol"]["value"])
        }
        self.name = "SubstrMatch_{}".format(
            molquerystr[query["queryMol"]["format"]])
        self.results = Container()
        self.done_count = Counter()
        self.input_size = Counter()
        qmol = sqlite.query_mol(query["queryMol"])
        pred = functools.partial(substr_filter, qmol, query["params"])
        self.append(nd.SQLiteReader(
            [sqlite.find_resource(t) for t in query["targets"]],
            fields=sqlite.merged_fields(query["targets"]),
            counter=self.input_size
        ))
        self.append(nd.UnpickleMolecule())
        self.append(ConcurrentFilter(pred, residue_counter=self.done_count))
        self.append(nd.AsyncMolDescriptor(static.MOL_DESC_KEYS))
        self.append(nd.AsyncMoleculeToJSON())
        self.append(nd.AsyncNumber("index", fields=[static.INDEX_FIELD]))
        self.append(nd.AsyncCountRows(self.done_count))
        self.append(nd.ContainerWriter(self.results))


class Superstruct(Workflow):
    def __init__(self, query, **kwargs):
        super().__init__(**kwargs)
        self.query = query
        molquerystr = {
            "molfile": "SDFile",
            "dbid": "{}{}".format(
                query["queryMol"]["source"], query["queryMol"]["value"])
        }
        self.name = "SuperstrMatch_{}".format(
            molquerystr[query["queryMol"]["format"]])
        self.results = Container()
        self.done_count = Counter()
        self.input_size = Counter()
        qmol = sqlite.query_mol(query["queryMol"])
        pred = functools.partial(supstr_filter, qmol, query["params"])
        self.append(nd.SQLiteReader(
            [sqlite.find_resource(t) for t in query["targets"]],
            fields=sqlite.merged_fields(query["targets"]),
            counter=self.input_size
        ))
        self.append(nd.UnpickleMolecule())
        self.append(ConcurrentFilter(pred, residue_counter=self.done_count))
        self.append(nd.AsyncMolDescriptor(static.MOL_DESC_KEYS))
        self.append(nd.AsyncMoleculeToJSON())
        self.append(nd.AsyncNumber("index", fields=[static.INDEX_FIELD]))
        self.append(nd.AsyncCountRows(self.done_count))
        self.append(nd.ContainerWriter(self.results))
