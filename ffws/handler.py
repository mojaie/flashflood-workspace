#
# (C) 2014-2017 Seiji Matsuoka
# Licensed under the MIT License (MIT)
# http://opensource.org/licenses/MIT
#

import glob
import gzip
import json
import os
import time

from chorus import v2000writer
from chorus.draw.svg import SVG
from chorus.model.graphmol import Compound
from chorus.util.text import decode
from tornado import gen
from tornado.options import options
from flashflood import static
from flashflood import auth
from flashflood.interface import xlsx
from flashflood.lod import ListOfDict

from ffws import configparser as conf
from ffws import sqlite
from ffws.workflow import activity
from ffws.workflow import chemdbfilter
from ffws.workflow import chemdbsearch
from ffws.workflow import gls
from ffws.workflow import profile
from ffws.workflow import similaritynetwork
from ffws.workflow import substructure
from ffws.workflow.responsetask import ResponseTask
from ffws.workflow import rdkitfmcs
from ffws.workflow import rdkitmorgan
from ffws.workflow.sdfparser import SDFParser


class BaseHandler(auth.BasicAuthHandler):
    def user_passwd_matched(self, user, passwd):
        return user in conf.USERS and passwd == conf.USERS[user]["password"]


class WorkflowHandler(BaseHandler):
    def initialize(self, workflow):
        super().initialize()
        self.workflow = workflow

    @auth.basic_auth
    @gen.coroutine
    def get(self):
        """Runs calculation job and immediately responds"""
        query = json.loads(self.get_argument("query"))
        task = ResponseTask(self.workflow(query))
        yield task.execute()
        self.write(task.response())


class ChemDBSearch(WorkflowHandler):
    def initialize(self):
        super().initialize(chemdbsearch.ChemDBSearch)


class Profile(WorkflowHandler):
    def initialize(self):
        super().initialize(profile.Profile)


class Activity(WorkflowHandler):
    def initialize(self):
        super().initialize(activity.Activity)


class ExactStruct(WorkflowHandler):
    def initialize(self):
        super().initialize(substructure.ExactStruct)


class AsyncWorkflowHandler(BaseHandler):
    def initialize(self, workflow, jobqueue, instance):
        super().initialize()
        self.workflow = workflow
        self.jobqueue = jobqueue

    @auth.basic_auth
    @gen.coroutine
    def get(self):
        """Submits calculation job"""
        query = json.loads(self.get_argument("query"))
        task = ResponseTask(self.workflow(query))
        yield self.jobqueue.put(task)
        self.write(task.response())


class ChemDBFilter(AsyncWorkflowHandler):
    def initialize(self, **kwargs):
        super().initialize(chemdbfilter.ChemDBFilter, **kwargs)


class Substruct(AsyncWorkflowHandler):
    def initialize(self, **kwargs):
        super().initialize(substructure.Substruct, **kwargs)


class Superstruct(AsyncWorkflowHandler):
    def initialize(self, **kwargs):
        super().initialize(substructure.Superstruct, **kwargs)


class GLS(AsyncWorkflowHandler):
    def initialize(self, **kwargs):
        super().initialize(gls.GLS, **kwargs)


class RDKitMorgan(AsyncWorkflowHandler):
    def initialize(self, **kwargs):
        super().initialize(rdkitmorgan.RDKitMorgan, **kwargs)


class RDKitFMCS(AsyncWorkflowHandler):
    def initialize(self, **kwargs):
        super().initialize(rdkitfmcs.RDKitFMCS, **kwargs)


class SimilarityNetworkHandler(BaseHandler):
    def initialize(self, workflow, jobqueue, instance):
        super().initialize()
        self.workflow = workflow
        self.jobqueue = jobqueue

    @gen.coroutine
    def post(self):
        """Submit similarity network calculation job"""
        js = json.loads(self.request.files['contents'][0]['body'].decode())
        params = json.loads(self.get_argument("params"))
        task = ResponseTask(self.workflow(js, params))
        yield self.jobqueue.put(task)
        self.write(task.response())


class GLSNetwork(SimilarityNetworkHandler):
    def initialize(self, **kwargs):
        super().initialize(similaritynetwork.GLSNetwork, **kwargs)


class RDKitMorganNetwork(SimilarityNetworkHandler):
    def initialize(self, **kwargs):
        super().initialize(similaritynetwork.RDKitMorganNetwork, **kwargs)


class RDKitFMCSNetwork(SimilarityNetworkHandler):
    def initialize(self, **kwargs):
        super().initialize(similaritynetwork.RDKitFMCSNetwork, **kwargs)


class SDFileParser(BaseHandler):
    @gen.coroutine
    def post(self):
        """Responds with datatable JSON made of query SDFile"""
        filename = self.request.files['contents'][0]['filename']
        contents = decode(self.request.files['contents'][0]['body'])
        params = json.loads(self.get_argument("params"))
        query = {
            "sourceFile": filename,
            "params": params
        }
        task = ResponseTask(SDFParser(contents, query))
        yield task.execute()
        self.write(task.response())


class WorkflowProgress(BaseHandler):
    def initialize(self, jobqueue, instance):
        super().initialize()
        self.jobqueue = jobqueue

    @auth.basic_auth
    @gen.coroutine
    def get(self):
        """Fetch calculation results"""
        query = json.loads(self.get_argument("query"))
        try:
            task = self.jobqueue.get(query["id"])
        except ValueError:
            try:
                p = os.path.join(
                    conf.TEMP_DIR, '{}.json.gz'.format(query["id"]))
                with gzip.open(p, 'rt') as f:
                    self.write(json.load(f))
            except OSError:
                self.write({
                    "workflowID": query["id"],
                    "status": "failure",
                    "reason": "job not found"
                })
        else:
            if query["command"] == "abort":
                self.jobqueue.abort(query["id"])
                while 1:
                    if task.status in ("done", "aborted"):
                        break
                    yield gen.sleep(0.5)
            self.write(task.response())


class StructurePreview(BaseHandler):
    @auth.basic_auth
    def get(self):
        """Structure image preview"""
        query = json.loads(self.get_argument("query"))
        try:
            qmol = sqlite.query_mol(query)
        except TypeError:
            response = '<span class="msg_warn">Format Error</span>'
        except ValueError:
            response = '<span class="msg_warn">Not found</span>'
        else:
            response = SVG(qmol).contents()
        self.write(response)


class SDFileExport(BaseHandler):
    def post(self):
        js = json.loads(self.request.files['contents'][0]['body'].decode())
        cols = [c["key"] for c in js["fields"]
                if c["visible"] and c["format"] in (
                    "text", "numeric", "d3_format", "compound_id")]
        mols = []
        for rcd in js["records"]:
            mol = Compound(json.loads(rcd["__moljson"]))
            for col in cols:
                mol.data[col] = rcd[col]
            mols.append(mol)
        text = v2000writer.mols_to_text(mols)
        self.set_header("Content-Type", 'text/plain; charset="utf-8"')
        self.write(text)


class ExcelExport(BaseHandler):
    def post(self):
        data = json.loads(self.request.files['contents'][0]['body'].decode())
        buf = xlsx.json_to_xlsx(data)
        self.set_header("Content-Type", 'application/vnd.openxmlformats-office\
                        document.spreadsheetml.sheet; charset="utf-8"')
        self.write(buf.getvalue())


class Schema(BaseHandler):
    @auth.basic_auth
    def get(self):
        """Responds with resource schema JSON

        :statuscode 200: no error
        """
        resources = []
        for r in conf.RESOURCES:
            # Server-side resource information
            rsrc = r.copy()
            rsrc.pop("resourceFile", None)
            rsrc.pop("resourceType", None)
            rsrc.pop("resourceURL", None)
            rsrc.pop("table", None)
            fields = ListOfDict()
            for f in rsrc["fields"]:
                if not f["key"].startswith("__"):
                    fields.add(f)
            if rsrc["domain"] == "chemical":
                fields.merge(static.MOL_DESC_FIELDS)
            rsrc["fields"] = list(fields)
            resources.append(rsrc)
        self.write({
            "resources": resources,
            "templates": conf.TEMPLATES,
            "compoundIDPlaceholder": conf.COMPID_PLACEHOLDER
        })


class ServerStatus(BaseHandler):
    def initialize(self, jobqueue, instance):
        super().initialize()
        self.jobqueue = jobqueue
        self.instance = instance

    @auth.basic_auth
    def get(self):
        js = {
            "instance": self.instance,
            "processors": static.PROCESSES,
            "queuedTasks": self.jobqueue.queue.qsize(),
            "debugMode": options.debug,
            "flashflood_version": static.VERSION,
            "workspace_version": conf.WORKSPACE_VERSION,
            "rdkit": static.RDK_AVAILABLE,
            "numericModule": static.NUMERIC_MODULE,
            "externalModules": [],
            "calc": {
                "fields": [
                    {"key": "workflowID", "format": "text"},
                    {"key": "name", "format": "text"},
                    {"key": "size", "d3_format": ".3s"},
                    {"key": "status", "format": "text"},
                    {"key": "created", "format": "date"}
                ],
                "records": []
            }
        }
        for ext in conf.EXTERNALS:
            rcd = {
                "name": ext.get("name", ext["module"]),
                "module": ext["module"]
            }
            if "base_url" in ext:
                rcd["base_url"] = ext["base_url"]
            js["externalModules"].append(rcd)
        for task in self.jobqueue.tasks_iter():
            js["calc"]["records"].append({
                "workflowID": task.id,
                "name": task.specs.name,
                "size": task.size(),
                "status": task.status,
                "created": time.strftime(
                    "%X %x %Z", time.localtime(task.creation_time))
            })
        for lpath in glob.glob(os.path.join(conf.TEMP_DIR, '*.json.gz')):
            with gzip.open(lpath, 'rt') as f:
                d = json.load(f)
            js["calc"]["records"].append({
                "workflowID": d["workflowID"],
                "name": d["name"],
                "size": os.path.getsize(lpath),
                "status": d["status"],
                "created": d["created"]
            })
        self.write(js)
