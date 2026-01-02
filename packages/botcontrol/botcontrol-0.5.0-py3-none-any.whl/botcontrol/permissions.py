class Permissions:
    def __init__(self):
        self.admins = set()

    def add_admin(self, user_id: int):
        self.admins.add(user_id)

    def is_admin(self, user_id: int) -> bool:
        return user_id in self.admins
