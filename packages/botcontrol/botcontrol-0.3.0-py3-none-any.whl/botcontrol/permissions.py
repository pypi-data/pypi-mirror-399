class Permissions:
    def __init__(self):
        self.owners = set()
        self.admins = set()

    def add_owner(self, user_id):
        self.owners.add(user_id)

    def add_admin(self, user_id):
        self.admins.add(user_id)

    def remove_owner(self, user_id):
        self.owners.discard(user_id)

    def remove_admin(self, user_id):
        self.admins.discard(user_id)

    def is_owner(self, user_id):
        return user_id in self.owners

    def is_admin(self, user_id):
        return user_id in self.admins
