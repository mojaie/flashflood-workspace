
import os
import sqlite3
import traceback

DATA_DIR = os.path.join(os.path.dirname(__file__), "../resources/")
DEST_PATH = os.path.join(DATA_DIR, "sdf_demo.sqlite3")
db_exists = os.path.exists(DEST_PATH)
con = sqlite3.connect(DEST_PATH)

# python3 sqlite3 module commits some update queries automatically
# even if it is in transaction. Set autocommit mode to avoid this feature.
con.isolation_level = None

cur = con.cursor()
cur.execute("PRAGMA page_size = 4096")
cur.execute("BEGIN")
cur2 = con.cursor()  # for query_gen

cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
dbs = [row[0] for row in cur.fetchall() if row[0] != "document"]

try:
    cur.execute("SELECT name FROM sqlite_master WHERE type='index'")
    idxs = [row[0] for row in cur.fetchall() if row[0].endswith("_mw")]
    for idx in idxs:
        cur.execute("DROP INDEX {}".format(idx))
        print("Drop index {} ...".format(idx))
    for db in dbs:
        cur.execute("CREATE INDEX {}_mw ON {}(_mw_wo_sw)".format(db, db))
        print("Create index {}_mw ...".format(db))
except KeyboardInterrupt:
    print("Abort: user cancel")
    con.rollback()
except Exception as e:
    print(traceback.format_exc())
    con.rollback()
else:
    con.commit()
    print("Cleaning up...")
    cur.execute("VACUUM")
con.close()
