from typing import Any

class Context:
    def __init__(self, user_id: int, message: str):
        self.user_id = user_id
        self.message = message
        self.data: dict[str, Any] = {}

    def send(self, text: str):
        print(f"[Bot -> {self.user_id}]: {text}")
