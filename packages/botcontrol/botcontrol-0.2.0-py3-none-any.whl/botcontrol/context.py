class Context:
    def __init__(self, adapter, chat_id, user_id):
        self.adapter = adapter
        self.chat_id = chat_id
        self.user_id = user_id

    async def send(self, text):
        await self.adapter.send_message(self.chat_id, text)
