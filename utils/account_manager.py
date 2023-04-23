class AccountManager:
    authorized = {1: [], 2: []}  # 1 - работник, 2 - администратор
    def __init__(self):
        pass

    def show(self):
        print(self.authorized)
    def get_access_level(self, user_id):
        print(self.authorized)
        if user_id in self.authorized[1]:
            return 1
        if user_id in self.authorized[2]:
            return 2
        return 0

    def auth(self, user_id, access_level):
        self.authorized[access_level].append(user_id)

    def unauth(self, user_id):
        access_level = self.get_access_level(user_id)
        if access_level != 0:
            self.authorized[access_level].remove(user_id)