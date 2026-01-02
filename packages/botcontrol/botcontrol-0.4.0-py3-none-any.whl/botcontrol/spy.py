class SpyEngine:
    def __init__(self, adapter=None):
        self.adapter = adapter

    def log(self, text: str):
        print(f"[SPY LOG] {text}")
