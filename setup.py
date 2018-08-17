
import json

from codecs import open
from os import path
from setuptools import setup, find_packages


here = path.abspath(path.dirname(__file__))

with open(path.join(here, "setup.json"), "rt") as f:
    setup_dict = json.load(f)["setuppy"]

with open(path.join(here, "README.md"), "rt", encoding="utf-8") as f:
    setup_dict["long_description"] = f.read()

setup_dict["packages"] = find_packages(exclude=["flashflood.test*"])

setup(**setup_dict)
