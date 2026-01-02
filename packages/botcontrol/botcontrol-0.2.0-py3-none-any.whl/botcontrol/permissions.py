class Permissions:
    def __init__(self, adapter):
        self.adapter = adapter

    async def is_owner(self, user_id):
        return user_id in self.adapter.owners

    async def is_admin(self, user_id):
        return user_id in self.adapter.admins
