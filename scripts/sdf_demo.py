
import json
import os
import pickle
import sqlite3
import traceback
import yaml
from chorus import descriptor, molutil, v2000reader


HERE = os.path.dirname(__file__)
DEST_FILE = "sdf_demo.sqlite3"
DEST_PATH = os.path.join(HERE, "../resources/{}".format(DEST_FILE))
SDF_DIR = os.path.join(HERE, "../raw/sdf_demo/")
with open(os.path.join(SDF_DIR, "info.yaml")) as f:
    SDF_INFO = yaml.load(f.read())
DBS = [s["id"] for s in SDF_INFO]

db_exists = os.path.exists(DEST_PATH)
con = sqlite3.connect(DEST_PATH)

# python3 sqlite3 module commits some update queries automatically
# even if it is in transaction. Set autocommit mode to avoid this feature.
con.isolation_level = None

cur = con.cursor()
cur.execute("PRAGMA page_size = 4096")
cur.execute("BEGIN")

domain = "chemical"

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
        "domain": domain,
        "name": "Local server API chemical database",
        "tables": []
    }
    for info in SDF_INFO:
        filename = info["filename"]
        table = info["table"]
        cols = info["columns"]
        # Append document
        td = {
            "id": info["id"],
            "entity": "{}:{}".format(DEST_FILE.split(".")[0], table),
            "name": info["name"],
            "columns": [],
            "placeholders": info.get("placeholders", ""),
            "description": info.get("description", "")
        }
        sort_type = {
            "real": "numeric", "integer": "numeric", "numeric": "numeric",
            "text": "text", "blob": "none"
        }
        for c in cols:
            name, type_ = c.split(" ")[:2]
            td["columns"].append({
                "key": name,
                "sort": sort_type[type_],
            })
        td["columns"].append({
            "key": "_mw_wo_sw",
            "name": "MW w/o salt and water",
            "sort": "numeric",
        })
        doc["tables"].append(td)
        # Insert records
        origins = info.get("origins", {})
        colsq = ["_mol blob", "_mw_wo_sw real"]
        colsq.extend(cols)
        path = os.path.join(SDF_DIR, filename)
        cur.execute("CREATE TABLE {} ({})".format(table, ", ".join(colsq)))
        print("Table created: {}".format(table))
        for i, mol in enumerate(v2000reader.mols_from_file(path)):
            descriptor.assign_valence(mol)
            molopts = mol.data
            mol.data = {}  # mol.options.clear() will affect molopts
            compressed = pickle.dumps(mol.jsonized(), protocol=4)
            qcols = [compressed, molutil.mw_wo_sw(mol)]
            for col in cols:
                colname = col.split(" ")[0]
                qcols.append(molopts.get(origins.get(colname, colname), ""))
            qs = ", ".join(["?"] * len(qcols))
            try:
                sql = "INSERT INTO {} VALUES ({})".format(table, qs)
                cur.execute(sql, qcols)
            except sqlite3.IntegrityError as e:
                if not info.get("suppress_warning", 0):
                    print("skip #{}: {}".format(i, e))
            if i and not i % 10000:
                print("{} rows processed...".format(i))
        cnt = cur.execute("SELECT COUNT(*) FROM {}".format(table))
        print("{} rows -> {}".format(cnt.fetchone()[0], table))
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
