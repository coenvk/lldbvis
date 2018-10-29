import json
import os


class BPL:
    def __init__(self):
        self.data = {"files": []}
        self.bplFile = os.path.expanduser('/home/arman') + '/.bpl'

    def addFile(self, name):
        self.data["files"].append({"name": name})

    def addBreakpoint(self, file_name, bp):
        contained = False
        for file in self.data["files"]:
            if file["name"] == file_name:
                file["breakpoints"].append(bp)
                contained = True
        if not contained:
            file_json = {"name": file_name, "breakpoints": [bp]}
            self.data["files"].append(file_json)

    def toJson(self):
        return json.dumps(self.data)

    def read(self):
        if os.path.isfile(self.bplFile):
            f = open(self.bplFile, 'r')
            with f:
                bpl_json = f.read()
                self.data = json.loads(bpl_json)

        return self.data

    def getFiles(self):
        return self.data["files"]

    def getBreakpoints(self, file_name):
        for file in self.data["files"]:
            if file["name"] == file_name:
                return file["breakpoints"]
        return []

    def setBreakpoints(self, file_name, bps):
        contained = False
        for file in self.data["files"]:
            if file["name"] == file_name:
                file["breakpoints"] = bps
                contained = True
        if not contained:
            file_json = {"name": file_name, "breakpoints": bps}
            self.data["files"].append(file_json)

    def save(self):
        f = open(self.bplFile, 'w')
        with f:
            f.write(json.dumps(self.data))
