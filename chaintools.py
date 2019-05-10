import hashlib
from os.path import exists
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding


class ChainTools:
    def load_public_key(self, public_key_serialization):
        return serialization.load_pem_public_key(public_key_serialization,
                                                 backend=default_backend())

    def encrypt(self, msg, public_key):
        return public_key.encrypt(msg, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()),
                                                    algorithm=hashes.SHA1(),
                                                    label=None))

    def verify(self, msg, signature, public_key):
        verifier = public_key.verifier(signature,
                                       padding.PSS(
                                           mgf=padding.MGF1(hashes.SHA256()),
                                           salt_length=padding.PSS.MAX_LENGTH),
                                       hashes.SHA256())
        verifier.update(msg)
        try:
            verifier.verify()
        except InvalidSignature:
            return False
        return True

    def serialize_byte(self, byteobject):
        outs = ''
        for e in bytearray(byteobject):
            outs += str(e) + '.'
        outs = outs[:-1]
        return outs

    def deserialize_byte(self, strobject):
        work = strobject.split('.')
        outs = bytearray()
        for e in work:
            try:
                outs.append(int(e))
            except ValueError:
                return None
        return bytes(outs)

    def hash_string(self, str):
        sha = hashlib.sha512()
        sha.update(str.encode())
        sha.digest()
        return sha.hexdigest()

    def is_keyfile_exist(self):
        return exists('Authorisation.dll')
