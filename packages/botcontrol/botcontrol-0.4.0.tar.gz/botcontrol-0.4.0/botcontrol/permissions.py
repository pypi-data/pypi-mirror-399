from typing import List

class Permissions:
    def __init__(self, adapter=None):
        self.adapter = adapter
        self.admins: List[int] = []

    def is_admin(self, user_id: int) -> bool:
        return user_id in self.admins

    def add_admin(self, user_id: int):
        if user_id not in self.admins:
            self.admins.append(user_id)
