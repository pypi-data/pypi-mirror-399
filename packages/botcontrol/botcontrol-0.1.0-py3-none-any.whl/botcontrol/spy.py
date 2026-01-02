# botcontrol/spy.py
from datetime import datetime

class SpyEngine:
    def __init__(self):
        self.logs = []

    def log(self, channel_id, author_id, action, detail=""):
        self.logs.append({
            "time": datetime.utcnow().isoformat(),
            "channel": channel_id,
            "author": author_id,
            "action": action,
            "detail": detail
        })

    def last(self, count=5):
        return self.logs[-count:]
