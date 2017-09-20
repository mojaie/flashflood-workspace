
import csv
import glob
import json
import os
import sqlite3
import traceback
import yaml


HERE = os.path.dirname(__file__)
RAW_FILES = glob.glob(os.path.join(HERE, "../raw/text_demo/*.txt"))
DEST_FILE = "text_demo.sqlite3"
DEST_PATH = os.path.join(HERE, "../resources/{}".format(DEST_FILE))

db_exists = os.path.exists(DEST_PATH)
con = sqlite3.connect(DEST_PATH)

# python3 sqlite3 module commits some update queries automatically
# even if it is in transaction. Set autocommit mode to avoid this feature.
con.isolation_level = None

cur = con.cursor()
cur.execute("PRAGMA page_size = 4096")
cur.execute("BEGIN")

domain = "activity"
data_type = {
    "inhibition%": "real",
    "IC50": "real",
    "flag": "integer"
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
        "domain": domain,
        "name": "Local server API activity database",
        "tables": []
    }
    for fi, filepath in enumerate(RAW_FILES):
        with open(filepath) as f:
            """ Create table """
            if f.readline() != '---\n':
                f.seek(0)
            schema = yaml.load(''.join(iter(f.readline, '---\n')))
            pk = schema.get("primary_key", "ID")
            entity = schema["entity"]
            sql_cols = [
                "{} text primary key check({} != '') collate nocase".format(
                    pk, pk)
            ]
            col_keys = [pk]
            for col in schema["columns"]:
                sql_dtype = data_type[col["valueType"]]
                sql_cols.append("{} {}".format(col["key"], sql_dtype))
                if "origin" in col:
                    col_keys.append(col["origin"])
                    del col["origin"]
                else:
                    col_keys.append(col["key"])
            sql = "CREATE TABLE {} ({})".format(entity, ", ".join(sql_cols))
            cur.execute(sql)
            print("Table created: {}".format(entity))
            """ Insert table contents """
            contents = f.read().strip().splitlines()
            reader = csv.DictReader(contents, delimiter="\t")
            for i, row in enumerate(reader):
                tc = "{} ({})".format(entity, ", ".join(col_keys))
                ph = ", ".join(["?"] * len(col_keys))
                sql_row = "INSERT INTO {} VALUES ({})".format(tc, ph)
                values = [row[c] for c in col_keys]
                try:
                    cur.execute(sql_row, values)
                except sqlite3.IntegrityError as e:
                    if not schema.get("suppress_warning", 0):
                        print("skip #{}: {}".format(i, e))
            cnt = cur.execute("SELECT COUNT(*) FROM {}".format(entity))
            print("{} rows -> {} ".format(cnt.fetchone()[0], entity))
            """ Put table info to the document """
            schema["entity"] = "{}:{}".format(DEST_FILE.split(".")[0], entity)
            schema["columns"].insert(0, {"key": pk, "sort": "text"})
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
