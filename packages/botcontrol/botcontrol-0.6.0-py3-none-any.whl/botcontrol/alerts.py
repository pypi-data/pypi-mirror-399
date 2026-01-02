class Alerts:
    def info(self, text: str):
        print(f"[INFO] {text}")

    def warning(self, text: str):
        print(f"[WARNING] {text}")

    def error(self, text: str):
        print(f"[ERROR] {text}")
