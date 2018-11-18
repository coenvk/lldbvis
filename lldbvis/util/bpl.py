import json
import os

_data = {"files": []}
_directory = os.path.expanduser('~')
_bpl_file = '/.bpl'


def set_working_dir(dir):
    os.chdir(dir)


def add_file(name):
    _data["files"].append({"name": name})


def add_breakpoint(file_name, bp):
    contained = False
    for file in _data["files"]:
        if file["name"] == file_name:
            file["breakpoints"].append(bp)
            contained = True
    if not contained:
        file_json = {"name": file_name, "breakpoints": [bp]}
        _data["files"].append(file_json)


def to_json():
    return json.dumps(_data)


def read():
    global _data
    file_path = str(_directory + _bpl_file)
    if os.path.isfile(file_path):
        f = open(file_path, 'r')
        with f:
            bpl_json = f.read()
            data = json.loads(bpl_json)

    _data = data
    return data


def get_files():
    return _data["files"]


def get_breakpoints(file_name):
    for file in _data["files"]:
        if file["name"] == file_name:
            return file["breakpoints"]
    return []


def set_breakpoints(file_name, bps):
    contained = False
    for file in _data["files"]:
        if file["name"] == file_name:
            file["breakpoints"] = bps
            contained = True
    if not contained:
        file_json = {"name": file_name, "breakpoints": bps}
        _data["files"].append(file_json)


def save():
    file_path = str(_directory + _bpl_file)
    f = open(file_path, 'w')
    with f:
        f.write(json.dumps(_data))
