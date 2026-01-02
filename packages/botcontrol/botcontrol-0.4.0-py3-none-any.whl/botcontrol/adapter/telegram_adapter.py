from .base_adapter import BaseAdapter

class TelegramAdapter(BaseAdapter):
    def __init__(self, token: str):
        self.token = token
        self.update_id = None

    async def send_message(self, chat_id: int, text: str) -> None:
        print(f"[Telegram] به {chat_id}: {text}")

    async def get_updates(self):
        return []

    async def handle_message(self, message):
        print("[Telegram] پیام دریافت شد:", message)
