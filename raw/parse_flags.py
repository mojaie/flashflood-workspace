
# coding: utf-8

# In[3]:


get_ipython().magic('matplotlib inline')

import csv
import collections
import importlib
import pprint
import io

output = ['''---
sql: >
  CREATE TABLE FREQHIT (
    ID text primary key check(ID != '') collate nocase,'''
]

with open("annotation_flags.csv") as f:
    reader = csv.DictReader(f)
    output.append(",\n".join("    {} integer".format(n) for n in reader.fieldnames) + "\n  )\n")
    output.append("id: freqhit")
    output.append("columns:")
    for n in reader.fieldnames:
        output.append("  - key: {}".format(n))
        output.append("    name: freqHit_{}".format(n))
        output.append("    tags: [{}]".format(n))
        output.append("    valueType: flag\n")
    output.append("---")
    output.append("{}\t{}".format("ID", "\t".join(reader.fieldnames)))
    records = {}
    for row in reader:
        for col, id_ in row.items():
            if id_ is None or id_ == "":
                continue
            if id_ not in records:
                records[id_] = []
            records[id_].append(col)
    for id_, cols in sorted(records.items(), key=lambda x: x[0]):
        row = "\t".join(str(int(n in cols)) for n in reader.fieldnames)
        output.append("{}\t{}".format(id_, row))

output.append("")
with open("../text_demo/annotation_flags.txt", "w") as f:
    f.write("\n".join(output))



