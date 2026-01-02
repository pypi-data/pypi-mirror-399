class Alerts:
    @staticmethod
    def info(text: str):
        print(f"[INFO] {text}")

    @staticmethod
    def warning(text: str):
        print(f"[WARNING] {text}")

    @staticmethod
    def error(text: str):
        print(f"[ERROR] {text}")
