
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

data_type = {
    "compound_id": "text",
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
        "id": "text_demo",
        "name": "text_demo",
        "domain": "activity",
        "type": "sqlite",
        "file": DEST_FILE,
        "description": "Default SQLite activity database",
        "resources": []
    }
    for fi, filepath in enumerate(RAW_FILES):
        """Create table"""
        rsrc = None
        contents = None
        with open(filepath) as f:
            if f.readline() != '---\n':
                f.seek(0)
            rsrc = yaml.load(''.join(iter(f.readline, '---\n')))
            contents = f.read().strip().splitlines()
        pk = rsrc.get("primary_key", "id")
        sqcols = []
        csv_keys = []
        sql_keys = []
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
                csv_keys.append(field["origin"])
                del field["origin"]
            else:
                csv_keys.append(field["key"])
            sql_keys.append(field["key"])
        sql = "CREATE TABLE {} ({})".format(rsrc["table"], ", ".join(sqcols))
        cur.execute(sql)
        print("Table created: {}".format(rsrc["table"]))
        """Insert table contents"""
        reader = csv.DictReader(contents, delimiter="\t")
        for i, row in enumerate(reader):
            sqflds = "{} ({})".format(rsrc["table"], ", ".join(sql_keys))
            ph = ", ".join(["?"] * len(sql_keys))
            sql_row = "INSERT INTO {} VALUES ({})".format(sqflds, ph)
            values = [row[c] for c in csv_keys]
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
