from passlib.hash import sha256_crypt

class AdminUtility:
    def verify(self, context, username, alleged_password):
        password_hash = context.application_database.get_admin_password(username)
        if password_hash is None:
            return False
        return sha256_crypt.verify(alleged_password, password_hash)
