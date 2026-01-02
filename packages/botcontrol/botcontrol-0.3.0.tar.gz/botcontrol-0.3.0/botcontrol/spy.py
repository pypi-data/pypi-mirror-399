class Spy:
    def __init__(self):
        self.logs = []

    def alert(self, message):
        """هشدار فوری"""
        print(f"[ALERT] {message}")
        self.logs.append(message)

    def get_logs(self):
        return self.logs
