
import glob
import os
import yaml

from flashflood.lod import ListOfDict


try:
    with open("config.yaml") as f:
        config = yaml.load(f.read())
except FileNotFoundError:
    """ use server_config stub"""
    config = {}


API_URL_PREFIX = config.get("api_url_prefix")
APP_BUNDLE_URL_PREFIX = config.get("app_bundle_url_prefix")
ASSETS_URL_PREFIX = config.get("assets_url_prefix")
INSTANCE_PREFIX = config.get("server_instance_prefix")

SPECS_BASE_DIR = config.get("specs_base_dir")
SQLITE_BASE_DIR = config.get("sqlite_base_dir")
REPORT_TEMPLATE_DIR = config.get("report_template_dir")
WEB_BUILD_DIR = config.get("web_build_dir")
WEB_DEBUG_BUILD_DIR = config.get("web_debug_build_dir")
WEB_ASSETS_DIR = config.get("web_assets_dir")

EXTERNALS = config.get("externals", [])

COMPID_PLACEHOLDER = config.get("compound_id_placeholder", "")
USERS = config.get("user")


RESOURCES = ListOfDict()
for filename in glob.glob(os.path.join(SPECS_BASE_DIR, "*.yaml")):
    with open(filename) as f:
        rsrc = yaml.load(f.read())
        RESOURCES.extend(rsrc)

TEMPLATES = ListOfDict()
for tm in glob.glob(os.path.join(REPORT_TEMPLATE_DIR, "*.csv")):
    TEMPLATES.append({
        "name": os.path.splitext(os.path.basename(tm))[0],
        "sourceFile": os.path.basename(tm)
    })
