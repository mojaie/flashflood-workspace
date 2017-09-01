
import csv
import glob
import json
import os
import sqlite3
import traceback
import yaml


HERE = os.path.dirname(__file__)
RAW_FILES = glob.glob(os.path.join(HERE, "../text_demo/*.txt"))
DEST_FILE = "text_demo.sqlite3"
DEST_PATH = os.path.join(HERE, "../{}".format(DEST_FILE))

db_exists = os.path.exists(DEST_PATH)
con = sqlite3.connect(DEST_PATH)

# python3 sqlite3 module commits some update queries automatically
# even if it is in transaction. Set autocommit mode to avoid this feature.
con.isolation_level = None

cur = con.cursor()
cur.execute("PRAGMA page_size = 4096")
cur.execute("BEGIN")

domain = "activity"

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
        "name": "Local server API activity database",
        "tables": []
    }
    for fi, filepath in enumerate(RAW_FILES):
        with open(filepath) as f:
            if f.readline() != '---\n':
                f.seek(0)
            schema = yaml.load(''.join(iter(f.readline, '---\n')))
            contents = f.read()
            cur.execute(schema["sql"])
            entity = schema["sql"].split(" ")[2]
            print("Table created: {}".format(entity))
            reader = csv.DictReader(contents.strip().splitlines(),
                                    delimiter="\t")
            for i, row in enumerate(reader):
                qs = ", ".join(["?"] * len(row))
                tc = "{} ({})".format(entity, ", ".join(row.keys()))
                try:
                    cur.execute("INSERT INTO {} VALUES ({})".format(tc, qs),
                                list(row.values()))
                except sqlite3.IntegrityError as e:
                    if not schema.get("suppress_warning", 0):
                        print("skip #{}: {}".format(i, e))
            cnt = cur.execute("SELECT COUNT(*) FROM {}".format(entity))
            print("{} rows -> {} ".format(cnt.fetchone()[0], entity))
            # put schema to document.tables
            schema["entity"] = "{}:{}".format(DEST_FILE.split(".")[0], entity)
            del schema["sql"]
            if "suppress_warning" in schema:
                del schema["suppress_warning"]
            doc["tables"].append(schema)
    # Save document
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
