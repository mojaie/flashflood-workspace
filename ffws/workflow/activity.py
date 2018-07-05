#
# (C) 2014-2018 Seiji Matsuoka
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


class Activity(Workflow):
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
            "assay_id", query["assay_id"], "=",
            fields=sqlite.merged_fields(sq_ids)
        )
        merge = nd.MergeRecords()
        self.connect(sq_filter, merge)
        cps = query.get("condition", {}).get("compounds", [])
        if cps:
            self.append(nd.Filter(lambda x: x["compound_id"] in cps))
        vtypes = query.get("condition", {}).get("value_types", ["IC50"])
        self.append(nd.Filter(lambda x: x["value_type"] in vtypes))
        fields = [{
            "key": "{}_{}".format(query["assay_id"], vt),
            "name": "{}:{}".format(query["assay_id"], vt),
            "format": "numeric"
        } for vt in vtypes]
        self.append(nd.Unstack(
            ["compound_id", "assay_id"], "value_type", "value",
            label_prefix="{}_".format(query["assay_id"]),
            fields=fields
        ))
        self.append(nd.Number("index", fields=[static.INDEX_FIELD]))
        self.append(nd.ContainerWriter(self.results))
