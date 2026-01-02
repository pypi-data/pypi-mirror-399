import json
import os

class Storage:
    def __init__(self, filename="data.json"):
        self.filename = filename
        if not os.path.exists(filename):
            with open(filename, "w") as f:
                json.dump({}, f)

    def read(self):
        with open(self.filename, "r") as f:
            return json.load(f)

    def write(self, data):
        with open(self.filename, "w") as f:
            json.dump(data, f, indent=4)

    def update(self, key, value):
        data = self.read()
        data[key] = value
        self.write(data)
