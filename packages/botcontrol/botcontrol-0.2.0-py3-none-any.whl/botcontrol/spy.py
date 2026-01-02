import asyncio

class SpyEngine:
    def __init__(self, adapter=None):
        self.adapter = adapter
        self.logs = []

    def log(self, text):
        self.logs.append(text)
        print(f"[LOG] {text}")

    def alert(self, text):
        if self.adapter and hasattr(self.adapter, "send_message"):
            for owner in self.adapter.owners:
                asyncio.create_task(self.adapter.send_message(owner, f"⚠️ ALERT: {text}"))
        print(f"[ALERT] {text}")
