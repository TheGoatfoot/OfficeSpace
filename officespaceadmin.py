from officespaceadminutility import AdminUtility


class Admin:
    service = None
    username = None
    id = None

    def __init__(self, service=None):
        self.service = service

    def verify(self, username, alleged_password):
        if AdminUtility().verify(self.service.context, username, alleged_password) is True:
            self.username = username
            self.id = self.service.context.application_database.get_admin_id(username)
            return True
        return False
