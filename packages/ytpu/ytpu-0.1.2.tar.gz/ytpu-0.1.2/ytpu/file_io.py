# file_io.py

import json


def load_json(path):
    with open(path, "r") as f:
        return json.load(f)


def write_json(path, data, mode="w"):
    with open(path, mode=mode) as f:
        json.dump(data, f, indent=4)
