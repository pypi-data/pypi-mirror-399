class SpyEngine:
    def __init__(self):
        self.logs = []

    def log(self, text: str):
        self.logs.append(text)
        print(f"[SPY] {text}")
