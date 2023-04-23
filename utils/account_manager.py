class AccountManager:
    authorized = {0: [], 1:[]}
    def __init__(self):
        pass

    def get_access_level(self, user_id):
        if user_id in self.authorized[0]:
            return 0
        if user_id in self.authorized[1]:
            return 1
        return -1

    def auth(self, user_id, access_level):
        self.authorized[access_level] = user_id

    def unauth(self, user_id):
        access_level = self.get_access_level(user_id)
        if access_level != -1:
            self.authorized[access_level].remove(user_id)