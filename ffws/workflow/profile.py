#
# (C) 2014-2017 Seiji Matsuoka
# Licensed under the MIT License (MIT)
# http://opensource.org/licenses/MIT
#

import os

from flashflood import static
from flashflood.core.workflow import Workflow
from flashflood.core.container import Container
import flashflood.node as nd

from ffws import configparser as conf
from ffws import sqlite


class Profile(Workflow):
    def __init__(self, query, **kwargs):
        super().__init__(**kwargs)
        self.query = query
        self.results = Container()
        sq_ids = []
        sq_rsrcs = []
        for target in query["targets"]:
            rsrc = conf.RESOURCES.find("id", target)
            if rsrc["resourceType"] == "sqlite":
                sq_ids.append(rsrc["id"])
                path = os.path.join(conf.SQLITE_BASE_DIR, rsrc["resourceFile"])
                sq_rsrcs.append((path, rsrc["table"]))
            """
            elif rsrc["resourceType"] == "screener_api":
                api.append(rsrc["resourceURL"])
            """
        sq_filter = nd.SQLiteReaderFilter(
            sq_rsrcs,
            "compound_id", query["compound_id"], "=",
            fields=sqlite.merged_fields(sq_ids)
        )
        merge = nd.MergeRecords()
        self.connect(sq_filter, merge)
        self.connect(merge, nd.Number("index", fields=[static.INDEX_FIELD]))
        self.append(nd.ContainerWriter(self.results))
