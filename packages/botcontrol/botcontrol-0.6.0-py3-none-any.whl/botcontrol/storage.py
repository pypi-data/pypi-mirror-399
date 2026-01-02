import json
from typing import Any

class Storage:
    def __init__(self, file_name: str = "storage.json"):
        self.file_name = file_name
        self.data: dict[str, Any] = {}
        self.load()

    def load(self):
        try:
            with open(self.file_name, "r") as f:
                self.data = json.load(f)
        except FileNotFoundError:
            self.data = {}

    def save(self):
        with open(self.file_name, "w") as f:
            json.dump(self.data, f, indent=2)

    def get(self, key: str, default=None):
        return self.data.get(key, default)

    def set(self, key: str, value: Any):
        self.data[key] = value
        self.save()
