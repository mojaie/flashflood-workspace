#
# (C) 2014-2018 Seiji Matsuoka
# Licensed under the MIT License (MIT)
# http://opensource.org/licenses/MIT
#

from flashflood.core.container import Container
from flashflood.core.workflow import Workflow
import flashflood.node as nd


class Assay(Workflow):
    def __init__(self, query):
        super().__init__()
        self.query = query
        self.name = "Assay"
        self.results = Container()
        self.append(nd.ContainerWriter(self.results))
