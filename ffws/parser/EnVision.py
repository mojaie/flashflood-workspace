
import csv


def content_loader(lines, rcnt=16, ccnt=24):
    """Load datafile from Envision.

    Args:
        path: input file path

    Returns:
        dict of parsed data.
    """
    blocks = []
    buf = []
    for row in csv.reader(lines, delimiter=","):
        if len(buf) and len(row) and row[0].startswith("Plate information"):
            blocks.append(buf)
            buf = []
        buf.append(row)
    blocks.append(buf)
    prev_barcode = None
    prev_layer = 0
    parsed = {"plates": []}
    for block in blocks:
        plate = {}
        plate["plateId"] = block[2][2]
        if plate["plateId"] == prev_barcode:
            plate["layerIndex"] = prev_layer + 1
        else:
            plate["layerIndex"] = 0
        plate["date"] = block[2][16]
        plate["wellValues"] = []
        rof = 2
        for i, row in enumerate(block):
            if row and row[0].startswith("Results"):
                rof += i
        for row in block[rof:rof+rcnt]:
            for cell in row[1:ccnt+1]:
                try:
                    value = float(cell)
                except ValueError:
                    value = "NaN"
                plate["wellValues"].append(value)
        parsed["plates"].append(plate)
        prev_barcode = plate["plateId"]
        prev_layer = plate["layerIndex"]
    return parsed


def file_loader(path, rcnt=16, ccnt=24):
    with open(path, encoding="UTF-8", newline="") as f:
        results = content_loader(f, rcnt, ccnt)
    return results
