import hashlib


class Helper:
    def hash_string(self, inp):
        sha = hashlib.sha512()
        sha.update(inp.encode('utf-8'))
        sha.digest()
        return sha.hexdigest()
