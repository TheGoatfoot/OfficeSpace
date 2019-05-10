import platform
import os.path

from chaintools import ChainTools


class ChainClient:
    application_name = None
    application_version = None
    application_key = ChainTools().load_public_key(ChainTools().deserialize_byte(
        '45.45.45.45.45.66.69.71.73.78.32.80.85.66.76.73.67.32.75.69.89.'
        '45.45.45.45.45.10.77.73.73.66.73.106.65.78.66.103.107.113.104.'
        '107.105.71.57.119.48.66.65.81.69.70.65.65.79.67.65.81.56.65.77.'
        '73.73.66.67.103.75.67.65.81.69.65.120.78.57.55.110.43.48.106.'
        '100.74.83.79.72.109.117.48.84.109.107.89.10.79.66.97.43.82.100.'
        '89.78.100.101.120.56.86.72.65.84.100.119.99.100.120.103.111.77.'
        '100.54.86.89.79.105.82.51.52.50.68.72.77.88.112.120.75.122.84.'
        '115.106.43.106.56.49.120.52.80.66.87.117.57.107.115.112.81.75.'
        '83.103.47.10.99.85.85.118.88.109.110.83.77.49.57.114.116.78.56.'
        '76.55.111.69.121.68.48.118.47.73.105.77.75.67.67.112.75.71.70.'
        '48.103.86.78.88.57.90.75.77.116.101.122.104.107.118.51.79.109.'
        '69.47.52.97.84.111.121.84.78.88.97.43.10.54.48.70.65.109.77.80.'
        '105.80.115.98.68.105.52.112.104.74.53.103.115.113.88.109.108.56.'
        '72.105.101.98.119.66.78.81.105.75.69.97.114.109.75.112.100.110.'
        '51.72.100.112.72.87.105.78.110.52.100.104.90.76.116.105.106.85.'
        '55.69.120.10.53.74.79.107.118.55.81.106.108.108.113.72.102.103.'
        '88.69.50.99.67.122.48.89.114.88.72.84.57.51.65.103.69.74.113.'
        '100.110.113.111.71.67.103.50.74.103.99.104.108.112.116.47.67.'
        '115.56.84.102.121.109.87.54.71.81.88.72.78.106.10.114.76.104.'
        '110.77.56.67.116.77.97.108.67.82.55.82.101.65.69.86.78.71.71.'
        '55.98.101.120.97.100.113.43.103.118.68.55.82.57.89.51.47.70.'
        '104.109.43.67.69.67.49.79.57.69.116.121.84.88.116.65.116.109.'
        '112.121.56.49.82.48.10.113.81.73.68.65.81.65.66.10.45.45.45.45.'
        '45.69.78.68.32.80.85.66.76.73.67.32.75.69.89.45.45.45.45.45.10'))

    def __init__(self, name, version_major):
        self.application_name = name
        self.application_version = version_major

    def get_application(self):
        return self.application_name + str(self.application_version)

    def get_uid(self):
        unameres = platform.uname()
        unique = unameres.machine + unameres.processor + \
            unameres.node + unameres.system + \
            unameres.version + unameres.release + \
            self.get_application()
        return ChainTools().hash_string(unique)

    def verify_key(self, key):
        try:
            return ChainTools().verify(self.get_uid().encode(), key, self.application_key)
        except TypeError:
            return False

    def is_keyfile_legit(self):
        if ChainTools().is_keyfile_exist() is False:
            return False
        if self.verify_key(open('Authorisation.dll', 'rb').read()) is False:
            os.remove('Authorisation.dll')
            return False
        return True

    def create_keyfile(self, code):
        if ChainTools().is_keyfile_exist():
            os.remove('Authorisation.dll')
        keyfile = open('Authorisation.dll', 'wb')
        keyfile.write(code)
        keyfile.close()
