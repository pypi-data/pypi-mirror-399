class Context:
    def __init__(self, user_id: int, chat_id: int = 0, message: str = ""):
        self.user_id = user_id
        self.chat_id = chat_id
        self.message = message

    async def send(self, text: str):
        print(f"[Message to {self.chat_id}] {text}")
