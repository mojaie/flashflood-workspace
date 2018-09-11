
import re

from chorus import v2000reader
from chorus import molutil
from tornado import httpclient


def rcdfetch(url, headers):
    http_client = httpclient.HTTPClient()
    request = httpclient.HTTPRequest(url)
    request.headers = headers
    try:
        res = http_client.fetch(request)
        rcd = compound_record(res.body.decode("utf-8"))
    except httpclient.HTTPError:
        rcd = {}
    finally:
        http_client.close()
    return rcd


def molfetch(url, headers):
    http_client = httpclient.HTTPClient()
    request = httpclient.HTTPRequest(url)
    request.headers = headers
    try:
        res = http_client.fetch(request)
        try:
            rcd = v2000reader.mol_from_text(res.body.decode("utf-8"))
        except ValueError:
            rcd = molutil.null_molecule()
    except httpclient.HTTPError:
        rcd = molutil.null_molecule()
    finally:
        http_client.close()
    return rcd


def compound_record(body):
    # TODO: refactor and add regex test
    res = {
        "entry": None,
        "name": [None],
        "formula": None,
        "remark": None,
        "comment": None,
        "reaction": [],
        "pathway": [],
        "module": [],
        "enzyme": [],
        "brite": None,
        "dblinks": []
    }

    # ENTRY
    entry = re.search(r"ENTRY +(C[0-9]+) +Compound", body)
    if entry is not None:
        res["entry"] = entry.group(1)
    # NAME
    names = re.search(r"NAME +([\w\W]*?)[\r\n][A-Z]", body)
    if names is not None:
        res["name"] = [s.strip() for s in names.group(1).split(";")]
    # FORMULA
    formula = re.search(r"FORMULA +(.*?)[\r\n]", body)
    if formula is not None:
        res["formula"] = formula.group(1)
    # REMARK
    remark = re.search(r"REMARK +(.*?)[\r\n]", body)
    if remark is not None:
        res["remark"] = remark.group(1)
    # COMMENT
    comment = re.search(r"COMMENT +(.*?)[\r\n]", body)
    if comment is not None:
        res["comment"] = comment.group(1)
    # REACTION
    react = re.search(r"REACTION +([\w\W]*?)[\r\n][A-Z]", body)
    if react is not None:
        res["reaction"] = [s.strip() for s in re.split("\W+", react.group(1))]
    # PATHWAY
    pathway = re.search(r"PATHWAY +([\w\W]*?)[\r\n][A-Z]", body)
    if pathway is not None:
        res["pathway"] = [s.strip() for s in pathway.group(1).split("\n")]
    # MODULE
    module = re.search(r"MODULE +([\w\W]*?)[\r\n][A-Z]", body)
    if module is not None:
        res["module"] = [s.strip() for s in module.group(1).split("\n")]
    # ENZYME
    enzyme = re.search(r"ENZYME +([\w\W]*?)[\r\n][A-Z]", body)
    if enzyme is not None:
        res["enzyme"] = [s.strip() for s in re.split("\s+", enzyme.group(1))]
    # BRITE
    brite = re.search(r"BRITE +([\w\W]*?)[\r\n][A-Z]", body)
    if brite is not None:
        res["brite"] = brite.group(1).strip()
    # DBLINKS
    dblinks = re.search(r"DBLINKS +([\w\W]*?)[\r\n][A-Z]", body)
    if dblinks is not None:
        dblkv = [s.strip().split(": ") for s in dblinks.group(1).split("\n")]
        res["dblinks"] = {d[0]: d[1] for d in dblkv}

    return res
