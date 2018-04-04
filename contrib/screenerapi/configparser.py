
import yaml


try:
    with open("config.yaml") as f:
        config = yaml.load(f.read())
except FileNotFoundError:
    """ use server_config stub"""
    config = {}


BASE_URL = config.get("screener_base_url")
USERS = config.get("user")
