from .base_adapter import BaseAdapter

class RubkaAdapter(BaseAdapter):
    async def send_message(self, user_id, text: str):
        print(f"[RubkaAdapter] To {user_id}: {text}")
