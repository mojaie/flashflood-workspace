#
# (C) 2014-2017 Seiji Matsuoka
# Licensed under the MIT License (MIT)
# http://opensource.org/licenses/MIT
#

from flashflood import static
from flashflood.core.container import Container
from flashflood.core.workflow import Workflow
import flashflood.node as nd

from ffws import sqlite


class ChemDBSearch(Workflow):
    def __init__(self, query, **kwargs):
        super().__init__(**kwargs)
        self.query = query
        self.name = "Search_queries[{}, ...]".format(query["values"][0])
        self.results = Container()
        self.append(nd.SQLiteReaderSearch(
            [sqlite.find_resource(t) for t in query["targets"]],
            query["key"], query["values"],
            fields=sqlite.merged_fields(query["targets"])
            ))
        self.append(nd.UnpickleMolecule())
        self.append(nd.MolDescriptor(static.MOL_DESC_KEYS))
        self.append(nd.MoleculeToJSON())
        self.append(nd.Number("index", fields=[static.INDEX_FIELD]))
        self.append(nd.ContainerWriter(self.results))
