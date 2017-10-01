
import glob
import json
import os
import pickle
import sqlite3
import traceback
import yaml
from chorus import descriptor, molutil, v2000reader

HERE = os.path.dirname(__file__)
RAW_FILES = glob.glob(os.path.join(HERE, "../raw/sdf_demo/*.sdf"))
DEST_FILE = "sdf_demo.sqlite3"
DEST_PATH = os.path.join(HERE, "../resources/{}".format(DEST_FILE))

db_exists = os.path.exists(DEST_PATH)
con = sqlite3.connect(DEST_PATH)

# python3 sqlite3 module commits some update queries automatically
# even if it is in transaction. Set autocommit mode to avoid this feature.
con.isolation_level = None

cur = con.cursor()
cur.execute("PRAGMA page_size = 4096")
cur.execute("BEGIN")

data_type = {
    "compound_id": "text",
    "text": "text",
    "numeric": "real",
    "count": "integer",
}

try:
    if db_exists:
        print("Truncate existing database ...")
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cur.fetchall()]
        for t in tables:
            cur.execute("DROP TABLE {}".format(t))
            print("Table {} dropped".format(t))
    cur.execute("CREATE TABLE document(document text)")
    doc = {
        "id": "sdf_demo",
        "name": "sdf_demo",
        "domain": "chemical",
        "type": "sqlite",
        "file": DEST_FILE,
        "description": "Default SQLite chemical database",
        "resources": []
    }
    for fi, filepath in enumerate(RAW_FILES):
        """Create table"""
        infopath = "{}.yaml".format(os.path.splitext(filepath)[0])
        rsrc = None
        with open(infopath) as f:
            rsrc = yaml.load(f)
        pk = rsrc.get("primary_key", "id")
        # _mol: pickled molecule object
        # _mw_wo_sw: MW for structure search prefilter
        sqcols = ["_mol blob", "_mw_wo_sw real"]
        sdf_keys = ["_mol", "_mw_wo_sw"]
        sql_keys = ["_mol", "_mw_wo_sw"]
        for field in rsrc["fields"]:
            sqtype = " {}".format(data_type[field["valueType"]])
            sqpk = ""
            if field["key"] == pk:
                sqpk = " primary key check({} != '')".format(pk)
            sqnocase = ""
            if field["valueType"] in ("text",):
                sqnocase = " collate nocase"
            sqcol = "".join((field["key"], sqtype, sqpk, sqnocase))
            sqcols.append(sqcol)
            if "origin" in field:
                sdf_keys.append(field["origin"])
                del field["origin"]
            else:
                sdf_keys.append(field["key"])
            sql_keys.append(field["key"])
        sql = "CREATE TABLE {} ({})".format(rsrc["table"], ", ".join(sqcols))
        cur.execute(sql)
        print("Table created: {}".format(rsrc["table"]))
        """Insert table contents"""
        for i, mol in enumerate(v2000reader.mols_from_file(filepath)):
            descriptor.assign_valence(mol)
            row = {
                "_mol": pickle.dumps(mol.jsonized(), protocol=4),
                "_mw_wo_sw": molutil.mw_wo_sw(mol)
            }
            row.update(mol.data)
            sqflds = "{} ({})".format(rsrc["table"], ", ".join(sql_keys))
            ph = ", ".join(["?"] * len(sql_keys))
            sql_row = "INSERT INTO {} VALUES ({})".format(sqflds, ph)
            values = [row[c] for c in sdf_keys]
            try:
                cur.execute(sql_row, values)
            except sqlite3.IntegrityError as e:
                if not rsrc.get("suppress_warning", 0):
                    print("skip #{}: {}".format(i, e))
            if i and not i % 10000:
                print("{} rows processed...".format(i))
        cnt = cur.execute("SELECT COUNT(*) FROM {}".format(rsrc["table"]))
        print("{} rows -> {}".format(cnt.fetchone()[0], rsrc["table"]))
        """ Put table info to the document """
        if "suppress_warning" in rsrc:
            del rsrc["suppress_warning"]
        doc["resources"].append(rsrc)
    """Save document"""
    cur.execute("INSERT INTO document VALUES (?)", (json.dumps(doc),))
except KeyboardInterrupt:
    print("User cancel")
    con.rollback()
except Exception as e:
    print(traceback.format_exc())
    con.rollback()
else:
    con.commit()
    print("Cleaning up...")
    cur.execute("VACUUM")
con.close()
