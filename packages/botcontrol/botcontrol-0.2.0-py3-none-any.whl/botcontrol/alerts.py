class Alerts:
    def __init__(self, adapter):
        self.adapter = adapter

    async def send_alert(self, chat_id, message):
        await self.adapter.send_message(chat_id, f"⚠️ ALERT: {message}")
