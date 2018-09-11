#
# (C) 2014-2017 Seiji Matsuoka
# Licensed under the MIT License (MIT)
# http://opensource.org/licenses/MIT
#

from flashflood.core.container import Container
from flashflood.core.workflow import Workflow
import flashflood.node as nd

from contrib.pubchem import configparser as conf



class PubChemCompound(Workflow):
    def __init__(self, query):
        super().__init__()
        self.query = query
        self.name = "Compound"
        self.results = Container()

        # merge assay summary
        # request2 = f"{conf.BASE_URL}compound/cid/{cid}/assaysummary/JSON"
        self.append(nd.ContainerWriter(self.results))

        # TODO: need to retr
