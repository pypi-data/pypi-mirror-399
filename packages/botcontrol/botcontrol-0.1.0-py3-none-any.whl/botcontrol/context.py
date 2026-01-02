class Context:
    def __init__(self, adapter, chat_id, user_id, text):
        self.adapter = adapter
        self.chat_id = chat_id
        self.user_id = user_id
        self.text = text

    async def send(self, text):
        await self.adapter.send_message(self.chat_id, text)

    async def kick(self, user_id):
        await self.adapter.kick_user(self.chat_id, user_id)

    async def get_admins(self):
        return await self.adapter.get_admins(self.chat_id)
