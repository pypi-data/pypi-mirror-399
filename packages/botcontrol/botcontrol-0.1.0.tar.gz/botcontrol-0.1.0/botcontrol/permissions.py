class Permissions:
    def __init__(self, adapter):
        self.adapter = adapter

    async def is_admin(self, chat_id, user_id):
        admins = await self.adapter.get_admins(chat_id)
        return user_id in admins if admins else False

    async def is_owner(self, chat_id, user_id):
        admins = await self.adapter.get_admins(chat_id)
        return admins and admins[0] == user_id
