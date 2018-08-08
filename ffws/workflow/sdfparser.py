#
# (C) 2014-2017 Seiji Matsuoka
# Licensed under the MIT License (MIT)
# http://opensource.org/licenses/MIT
#

from flashflood import static
from flashflood.core.container import Container
from flashflood.core.workflow import Workflow
import flashflood.node as nd


class SDFParser(Workflow):
    def __init__(self, contents, query, **kwargs):
        super().__init__(**kwargs)
        self.query = query
        self.name = query["sourceFile"]
        self.results = Container()
        self.append(nd.SDFileLinesInput(
            contents, sdf_options=query["params"]["fields"],
            fields=[
                {"key": q, "name": q, "format": "text"}
                for q in query["params"]["fields"]
            ]
        ))
        self.append(nd.MolDescriptor(static.MOL_DESC_KEYS))
        self.append(nd.MoleculeToJSON())
        self.append(nd.Number("index", fields=[static.INDEX_FIELD]))
        self.append(nd.ContainerWriter(self.results))
