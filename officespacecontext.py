import logging
import os.path
import time

from officespaceserver import Server
from officespacedatabase import Database
from chainclient import ChainClient
from officespacerent import Rent


class Context:
    # Properties
    application_info = None
    log_user = None
    log_application = None
    application_active = None
    application_database = None
    application_drm = None
    application_drm_check = None
    application_server = None
    application_rent = None
    service_list = None
    session = None

    def __init__(self):
        # Initialize
        #   Data
        self.application_info = {
            'application_name': 'OfficeSpace',
            'application_version_major': 1,
            'application_version_minor': 0,
            'application_version_revision': 0,
        }
        #   Logging
        #       Formatter
        log_formatter = logging.Formatter('%(asctime)-15s %(levelname)-8s %(message)s')
        #       File Handler
        if os.path.isdir('logs') is False:
            os.makedirs('logs')
        #           User
        log_user_filehandler = logging.FileHandler('logs/log_user.txt')
        log_user_filehandler.setLevel(logging.INFO)
        log_user_filehandler.setFormatter(log_formatter)
        #           Application
        log_application_filehandler = logging.FileHandler('logs/log_application.txt')
        log_application_filehandler.setLevel(logging.INFO)
        log_application_filehandler.setFormatter(log_formatter)
        #       Logger
        #           User
        self.log_user = logging.getLogger('user')
        self.log_user.setLevel(logging.INFO)
        self.log_user.addHandler(log_user_filehandler)
        #           Application
        self.log_application = logging.getLogger('application')
        self.log_application.setLevel(logging.INFO)
        self.log_application.addHandler(log_application_filehandler)
        # Variables
        self.application_active = True
        self.application_drm_check = False
        # Database
        self.application_database = Database('database.db')
        # DRM
        self.application_drm = ChainClient(self.application_info.get('application_name'),
                                           str(self.application_info.get('application_version_major')))
        # Websocket
        self.application_server = Server(self)
        # Certificate
        if os.path.isdir('cert') is False:
            os.makedirs('cert')
        # Services
        self.service_list = []
        # Rent
        self.application_rent = Rent(self)
        # Session
        self.session = str(int(time.time()))

    def start_server(self):
        self.application_server.start()

    def stop_server(self):
        self.application_server.stop()
