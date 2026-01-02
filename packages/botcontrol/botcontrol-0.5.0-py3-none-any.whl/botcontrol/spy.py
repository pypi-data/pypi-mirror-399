class SpyEngine:
    def __init__(self):
        self.logs = []

    def log(self, message: str):
        self.logs.append(message)
        print(f"[Spy] {message}")
