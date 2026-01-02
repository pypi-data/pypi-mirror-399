import json

class Storage:
    def __init__(self, file="storage.json"):
        self.file = file
        self.data = {}
        self.load_all()

    def save(self, key, value):
        self.data[key] = value
        self._write()

    def load(self, key):
        return self.data.get(key)

    def _write(self):
        with open(self.file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)

    def load_all(self):
        try:
            with open(self.file, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        except:
            self.data = {}
