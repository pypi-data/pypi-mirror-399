from typing import Any

class BotContext:
    def __init__(self, user_id: int, message: str, adapter: Any):
        self.user_id = user_id
        self.message = message
        self.adapter = adapter

    async def send(self, text: str):
        await self.adapter.send_message(self.user_id, text)
