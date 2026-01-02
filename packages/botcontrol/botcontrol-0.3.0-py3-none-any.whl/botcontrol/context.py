class Context:
    def __init__(self, user_id, message, bot):
        self.user_id = user_id
        self.message = message
        self.bot = bot

    def reply(self, text):
        """ارسال پیام به کاربر"""
        if hasattr(self.bot, "adapter"):
            self.bot.adapter.send_message(self.user_id, text)
        else:
            print(f"[Reply to {self.user_id}]: {text}")
