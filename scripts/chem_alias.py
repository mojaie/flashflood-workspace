
import os
import pickle
import sqlite3
import traceback

from chorus import molutil, substructure

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
dbs = [row[0] for row in cur.fetchall() if row[0] != "MASTER"]


def query_gen():
    for dbq in dbs:
        for row in cur2.execute("SELECT ID, _mol FROM {}".format(dbq)):
            yield row

try:
    for db in dbs:
        cur.execute(
            "ALTER TABLE {} ADD COLUMN _aliases text DEFAULT ''".format(db))
        cur.execute("CREATE INDEX {}_mw ON {}(_mw_wo_sw)".format(db, db))
    for q in query_gen():
        qid, qmol = q
        qmol = pickle.loads(qmol)
        aliases = set()
        for db in dbs:
            sql = "SELECT ID, _mol FROM {} WHERE _mw_wo_sw = {} \
".format(db, molutil.mw_wo_sw(qmol))
            for row in cur.execute(sql):
                rid, rmol = row
                rmol = pickle.loads(rmol)
                if substructure.equal(qmol, rmol) and qid != rid:
                    aliases.add(rid)
        atxt = ", ".join(aliases)
        if aliases:
            cur.execute("UPDATE {} SET _aliases = '{}' WHERE ID = '{}' \
".format(db, atxt, qid))
            print("set aliases: {} -> {}".format(qid, atxt))

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
