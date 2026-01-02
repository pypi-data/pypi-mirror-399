from .base_adapter import BaseAdapter

class TelegramAdapter(BaseAdapter):
    async def send_message(self, user_id, text: str):
        print(f"[TelegramAdapter] To {user_id}: {text}")
