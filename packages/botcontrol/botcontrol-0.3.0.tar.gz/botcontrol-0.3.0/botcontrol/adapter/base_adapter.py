# botcontrol/adapter/base_adapter.py
class BaseAdapter:
    """
    Template عمومی برای Adapter سایر ربات‌ها.
    برای ساخت Adapter جدید از این کلاس ارث‌بری کن.
    """
    async def send_message(self, chat_id, text):
        """ارسال پیام به چت"""
        raise NotImplementedError

    async def get_user_id(self, message):
        """گرفتن آیدی کاربر از پیام"""
        raise NotImplementedError

    async def get_chat_id(self, message):
        """گرفتن آیدی چت از پیام"""
        raise NotImplementedError

    async def listen(self, callback):
        """لیست کردن پیام‌ها و ارسال به BotControl"""
        raise NotImplementedError
