
# coding: utf-8

# In[5]:


import glob
import json
import pickle
import time

from kiwiii.parser import BiacoreT200
from vega import Vega

data = []
for f in glob.glob("instruments/BiacoreT200/*.txt"):
    conc = int(f.split("_C")[1].split(".")[0])
    series = [
        {"conc": conc/16},
        {"conc": conc/8},
        {"conc": conc/4},
        {"conc": conc/2},
        {"conc": conc}
    ]
    rcds = BiacoreT200.file_loader(f, series)
    data.append(rcds)

specｓ = BiacoreT200.dose_specs()
specs["data"][0]["transform"] = [
    {"type": "formula", "as": "corrected", "expr": "datum.value - 1000"}
]
specs["scales"][0]["domain"] = [0, 180]
specs["scales"][1]["domain"] = [-5, 25]
specs["axes"][0]["values"] = [0, 60, 120, 180]
specs["axes"][1]["tickCount"] = 5
specs["marks"][0]["marks"][0]["encode"]["enter"]["y"]["field"] = "corrected"


ids = [
    "DB00186",
    "DB00189",
    "DB00193",
    "DB00203",
    "DB00764",
    "DB00863",
    "DB00865",
    "DB00868",
    "DB01143",
    "DB01240",
    "DB01242",
    "DB01361",
    "DB01366",
    "DB02959"
]

mapping = {
    "created": time.strftime("%X %x %Z", time.localtime(time.time())),
    "column": {
        "key": "sensorgram",
        "name": "Sensorgram",
        "sort": "none",
        "valueType": "plot",
        "visible": True
    },
    "key": "ID",
    "mapping": {}
}

for i, d in zip(ids, data):
    sp = pickle.loads(pickle.dumps(specs))
    specs["data"][0]["values"] = d
    mapping["mapping"][i] = sp

with open("biaResult.json", "w") as f:
    json.dump(mapping, f)

