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


def rdmorgan_calc(qmol, radius, row):
    try:
        row["morgan_sim"] = rdkit.morgan_sim(row["__molobj"], qmol, radius)
    except:
        print(traceback.format_exc())
        return
    return row


def thld_filter(thld, row):
    return row["morgan_sim"] >= thld


class RDKitMorgan(Workflow):
    def __init__(self, query, **kwargs):
        super().__init__(**kwargs)
        self.query = query
        thld = float(query["params"]["threshold"])
        molquerystr = {
            "molfile": "SDFile",
            "dbid": "{}{}".format(
                query["queryMol"]["source"], query["queryMol"]["value"])
        }
        self.name = "MorganD4Jaccard>={}_{}".format(
            thld, molquerystr[query["queryMol"]["format"]])
        self.results = Container()
        self.done_count = Counter()
        self.input_size = Counter()
        self.append(nd.SQLiteReader(
            [sqlite.find_resource(t) for t in query["targets"]],
            fields=sqlite.merged_fields(query["targets"]),
            counter=self.input_size
        ))
        self.append(nd.UnpickleMolecule())
        # radius=2 is ECFP4 equivalent
        qmol = sqlite.query_mol(query["queryMol"])
        self.append(ConcurrentFilter(
            functools.partial(thld_filter, thld),
            func=functools.partial(rdmorgan_calc, qmol, 2),
            residue_counter=self.done_count,
            fields=[
                {"key": "morgan_sim", "name": "Fingerprint similarity",
                 "d3_format": ".2f"}
            ]
        ))
        self.append(nd.AsyncMolDescriptor(static.MOL_DESC_KEYS))
        self.append(nd.AsyncMoleculeToJSON())
        self.append(nd.AsyncNumber("index", fields=[static.INDEX_FIELD]))
        self.append(nd.AsyncCountRows(self.done_count))
        self.append(nd.ContainerWriter(self.results))
