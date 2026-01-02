import json
from typing import Any

class Storage:
    def __init__(self):
        self.data: dict = {}

    def save(self, key: str, value: Any):
        self.data[key] = value

    def load(self, key: str) -> Any:
        return self.data.get(key)

    def save_to_file(self, filename: str):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)

    def load_from_file(self, filename: str):
        with open(filename, "r", encoding="utf-8") as f:
            self.data = json.load(f)
