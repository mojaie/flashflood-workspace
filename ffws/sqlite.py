#
# (C) 2014-2017 Seiji Matsuoka
# Licensed under the MIT License (MIT)
# http://opensource.org/licenses/MIT
#

import os
import pickle

from chorus import smilessupplier, v2000reader
from chorus.draw import calc2dcoords
from chorus.model.graphmol import Compound
from flashflood import lod
from flashflood.interface import sqlite

from ffws import configparser as conf


def find_resource(resource_id):
    rsrc = conf.RESOURCES.find("id", resource_id)
    path = os.path.join(conf.SQLITE_BASE_DIR, rsrc["resourceFile"])
    return path, rsrc["table"]


def resources(domain=None):
    rsrcs = lod.filtered(conf.RESOURCES, "resourceType", "sqlite")
    if domain is not None:
        rsrcs = lod.filtered(rsrcs, "domain", domain)
    for rsrc in rsrcs:
        path = os.path.join(conf.SQLITE_BASE_DIR, rsrc["resourceFile"])
        yield path, rsrc["table"]


def merged_fields(rsrc_ids):
    results = lod.ListOfDict()
    for r in rsrc_ids:
        rsrc = conf.RESOURCES.find("id", r)
        results.merge(rsrc["fields"])
    return results


def query_mol(query):
    if query["format"] == "smiles":
        try:
            qmol = smilessupplier.smiles_to_compound(query["value"])
            calc2dcoords.calc2dcoords(qmol)
        except (ValueError, StopIteration):
            raise TypeError()
    elif query["format"] == "molfile":
        try:
            qmol = v2000reader.mol_from_text(query["value"])
        except (ValueError, StopIteration):
            raise TypeError()
    elif query["format"] == "dbid":
        file_, table = find_resource(query["source"])
        conn = sqlite.Connection(file_)
        res = conn.find_first(table, "compound_id", query["value"])
        if res is None:
            raise ValueError()
        qmol = Compound(pickle.loads(res["__molpickle"]))
    return qmol
