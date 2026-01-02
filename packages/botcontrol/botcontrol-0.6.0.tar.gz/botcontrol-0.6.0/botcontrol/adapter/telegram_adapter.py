from .base_adapter import BaseAdapter
from ..context import Context

class TelegramAdapter(BaseAdapter):
    def send_message(self, context: Context, text: str):
        print(f"[Telegram -> {context.user_id}]: {text}")

    def receive_message(self):
        return {"user_id": 2, "message": "سلام از تلگرام"}
