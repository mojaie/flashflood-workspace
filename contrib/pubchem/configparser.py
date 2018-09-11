
import yaml


try:
    with open("config.yaml") as f:
        config = yaml.load(f.read())
except FileNotFoundError:
    """ use server_config stub"""
    config = {}


BASE_URL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/"
