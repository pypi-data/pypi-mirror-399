from .base_adapter import BaseAdapter

class RubkaAdapter(BaseAdapter):
    async def send_message(self, chat_id: int, text: str) -> None:
        print(f"[Rubka] به {chat_id}: {text}")

    async def get_updates(self):
        return []

    async def handle_message(self, message):
        print("[Rubka] پیام دریافت شد:", message)
