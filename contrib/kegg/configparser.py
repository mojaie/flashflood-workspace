
import yaml


try:
    with open("config.yaml") as f:
        config = yaml.load(f.read())
except FileNotFoundError:
    """ use server_config stub"""
    config = {}


BASE_URL = next(filter(
    lambda x: x["module"] == "contrib.kegg", config["externals"]
))["base_url"]
