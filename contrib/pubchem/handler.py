
import json
import pickle

from chorus import v2000writer
from chorus.model.graphmol import Compound
from tornado import web
from flashflood.interface import sqlite as sq

from ffws import handler
from ffws import sqlite
from contrib.pubchem import parser
from contrib.pubchem import configparser as conf
from contrib.pubchem.workflow.compound import PubChemCompound
from contrib.pubchem.workflow.bioassay import PubChemBioAssay


class ExactSmilesHandler(web.RequestHandler):
    """Retrieve CIDs of compounds which are exactly same as the query molecule.
    """
    def get(self, query):
        q = f"{conf.BASE_URL}compound/fastidentity/smiles/{query}/cids/JSON"
        res = parser.fetch(q)
        rcds = json.loads(res)["IdentifierList"]["CID"]
        self.write(json.dumps(rcds))


class ExactIdHandler(web.RequestHandler):
    """Retrieve CIDs of compounds which are exactly same as the query molecule.
    """
    def get(self, query):
        for file_, table in sqlite.resources(domain="chemical"):
            conn = sq.Connection(file_)
            res = conn.find_first(table, "compound_id", query)
            if res is not None:
                mol = Compound(pickle.loads(res["__molpickle"]))
                ctxt = v2000writer.mols_to_text([mol])
                break
        if res is None:
            self.write({"error": "Invalid query"})
            return
        query = f"{conf.BASE_URL}compound/fastidentity/sdf/cids/JSON"
        res = parser.fetch_post(query, {"sdf": ctxt})
        rcds = json.loads(res)["IdentifierList"]["CID"]
        self.write(json.dumps(rcds))


class ExactSdfHandler(web.RequestHandler):
    """Retrieve CIDs of compounds which are exactly same as the query molecule.
    """
    def post(self):
        ctxt = json.loads(self.get_argument("query"))["sdf"]
        query = f"{conf.BASE_URL}compound/fastidentity/sdf/cids/JSON"
        res = parser.fetch_post(query, {"sdf": ctxt})
        rcds = json.loads(res)["IdentifierList"]["CID"]
        self.write(json.dumps(rcds))


class CompoundHandler(handler.AsyncWorkflowHandler):
    """Retrieve compound properties and assay descs by PubChem CID
    """
    def initialize(self, **kwargs):
        super().initialize(PubChemCompound, **kwargs)


class BioAssayHandler(handler.WorkflowHandler):
    """Retrieve assay summaries by PubChem AID
    """
    def initialize(self):
        super().initialize(PubChemBioAssay)


def install(application, **kwargs):
    application.add_handlers(r".*", [
        (r"/pubchem/exact/sdf", ExactSdfHandler),
        (r"/pubchem/exact/id/(.*)", ExactIdHandler),
        (r"/pubchem/exact/smiles/(.*)", ExactSmilesHandler),
        (r"/pubchem/compound", CompoundHandler)
    ])
