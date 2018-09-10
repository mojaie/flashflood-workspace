#
# (C) 2014-2018 Seiji Matsuoka
# Licensed under the MIT License (MIT)
# http://opensource.org/licenses/MIT
#

from flashflood.core.container import Container
from flashflood.core.workflow import Workflow
import flashflood.node as nd


def queryString(query):
    ls = []
    for k, v in query.items():
        ls.append("{}={}".format(k, v))
    return "&".join(ls)


class Pathway(Workflow):
    def __init__(self, query):
        super().__init__()
        self.query = query
        self.name = f"KEGG pathway"
        self.results = Container()
        self.append(nd.ContainerWriter(self.results))
