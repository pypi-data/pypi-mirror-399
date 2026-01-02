import json
import time

class Storage:
    def __init__(self, filename="botcontrol_logs.json"):
        self.filename = filename

    def save(self, data):
        data["time"] = int(time.time())
        with open(self.filename, "a", encoding="utf-8") as f:
            f.write(json.dumps(data, ensure_ascii=False) + "\n")
