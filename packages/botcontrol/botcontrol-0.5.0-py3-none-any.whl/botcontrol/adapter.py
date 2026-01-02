from .context import Context

class Adapter:
    """
    Adapter برای اتصال BotControl به هر پلتفرم
    """

    def __init__(self, bot):
        self.bot = bot

    def send_message(self, user_id, text):
        """ارسال پیام به کاربر"""
        print(f"[Adapter] Sending to {user_id}: {text}")

    def receive_message(self, user_id, text):
        """دریافت پیام از کاربر و اجرای دستورات"""
        context = Context(user_id, text, self.bot)
        command_name = text.split()[0]
        result = self.bot.engine.execute(command_name, context)
        if result:
            self.send_message(user_id, result)
