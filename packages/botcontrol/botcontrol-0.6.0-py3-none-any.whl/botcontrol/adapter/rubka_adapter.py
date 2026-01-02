from .base_adapter import BaseAdapter
from ..context import Context

class RubkaAdapter(BaseAdapter):
    def send_message(self, context: Context, text: str):
        print(f"[Rubka -> {context.user_id}]: {text}")

    def receive_message(self):
        # فقط نمونه لوکال
        return {"user_id": 1, "message": "سلام از روبیکا"}
