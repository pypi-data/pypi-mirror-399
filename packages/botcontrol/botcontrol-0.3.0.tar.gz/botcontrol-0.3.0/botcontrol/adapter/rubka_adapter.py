# botcontrol/adapter/rubka_adapter.py
from .base_adapter import BaseAdapter

class RubkaAdapter(BaseAdapter):
    """
    Adapter مخصوص Rubka.
    این کلاس پیام‌ها رو از Rubka میگیره و به BotControl میفرسته
    و دستورات کتابخونه بدون وابستگی مستقیم اجرا میشن.
    """
    def __init__(self, client):
        self.client = client

    async def send_message(self, chat_id, text):
        """ارسال پیام به چت"""
        await self.client.send_message(chat_id, text)

    async def get_user_id(self, message):
        """گرفتن آیدی کاربر از پیام"""
        return message.author_guid

    async def get_chat_id(self, message):
        """گرفتن آیدی چت از پیام"""
        return message.peer_id

    async def listen(self, callback):
        """لیست کردن پیام‌ها و ارسال به BotControl"""
        @self.client.on_message()
        async def handler(message):
            data = {
                "user_id": await self.get_user_id(message),
                "text": message.text,
                "chat_id": await self.get_chat_id(message),
                "message_obj": message
            }
            await callback(data)
