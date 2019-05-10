import threading
import json
import sched
import time

from autobahn.twisted.websocket import WebSocketServerProtocol
from officespaceadmin import Admin


class ServerService(WebSocketServerProtocol):
    context = None
    connection_count = 0

    admin = None
    verification_thread = None
    ping_thread = None
    request = None

    def log_user(self, inp):
        try:
            log = 'Session '+self.context.session+' ['+str(self.connection_count)+' - '+str(self.request.peer)+'] '+inp
        except AttributeError:
            log = 'Mingebag'
        ServerService.context.log_user.info(log)

    def onConnect(self, request):
        ServerService.connection_count += 1
        self.connection_count = ServerService.connection_count
        self.admin = Admin(self)
        self.request = request
        self.log_user('Connection')
        # Start verification countdown
        self.verification_thread = threading.Timer(10.0, self.verify)
        self.verification_thread.start()
        # Start ping thread
        self.ping_thread = threading.Timer(5.0, self.ping)
        self.ping_thread.start()

    def onOpen(self):
        self.log_user('Open')

    def onMessage(self, payload, is_binary):
        json_input = json.loads(str(payload, 'utf-8'))
        if self.is_sensitive(json_input):
            self.log_user('Received sensitive information.')
        else:
            self.log_user('Message - '+str(payload))
        self.handle_command(json_input)

    def onClose(self, was_clean, code, reason):
        if self.admin is not None:
            self.log_user('Close :' + reason)
            self.verification_thread.cancel()
            self.ping_thread.cancel()
            if self in ServerService.context.service_list:
                ServerService.context.service_list.remove(self)
        else:
            self.log_user('Closed unidentified connection.')

    def verify(self):
        if self.admin.username is None:
            self.log_user('Unable to give verification and is kicked.')
            self.sendClose(1000, 'Unable to give identification!')
            return False
        return True

    def ping(self):
        self.sendPing(b'ping')
        # Start over
        self.ping_thread = threading.Timer(5.0, self.ping)
        self.ping_thread.start()

    def is_sensitive(self, json_input):
        if 'sensitive' not in json_input:
            return False
        return json_input['sensitive']

    def send(self, command, content):
        self.sendMessage(bytes(json.dumps({'command': command, 'content': content}), 'utf-8'))

    # Commands
    #   Login
    def command_login(self, json_input):
        for a in self.context.service_list:
            if a.admin.username == json_input['username']:
                self.sendClose(1000, 'User is logged in!')
                return
        login_attempt = self.admin.verify(json_input['username'], json_input['password'])
        if login_attempt is True:
            self.log_user('Login as ' + self.admin.username)
            ServerService.context.service_list.append(self)
            self.send('login', 'ok')
            return
        else:
            self.send('login', 'fail')
            self.log_user('Login failed.')
        self.sendClose(1000, 'Incorrect login data!')

    #   Client
    def command_get_client(self, json_input):
        self.log_user('Requesting client data.')
        self.send('get_client', self.context.application_database.get_client(json_input['name']))

    def command_add_client(self, json_input):
        self.log_user('Inserting client...')
        processed_input = (json_input['name'], json_input['pob'], json_input['dob'], json_input['gender'],
                           json_input['occupation'], json_input['address'], json_input['religion'],
                           json_input['married'], self.admin.id)
        if self.context.application_database.insert_client(processed_input) is False:
            self.log_user('Fail to insert!')
            self.send('add_client', 'fail')
        else:
            self.log_user('Insert successful!')
            self.send('add_client', 'ok')

    def command_edit_client(self, json_input):
        self.log_user('Editing client...')
        processed_input = (json_input['name'], json_input['pob'], json_input['dob'], json_input['gender'],
                           json_input['occupation'], json_input['address'], json_input['religion'],
                           json_input['married'], json_input['id'])
        if self.context.application_database.edit_client(processed_input) is False:
            self.log_user('Fail to edit!')
            self.send('edit_client', 'fail')
        else:
            self.log_user('Edit successful!')
            self.send('edit_client', 'ok')

    #   Rent
    def command_create_rent(self, json_input):
        self.log_user('Creating rent...')
        processed_input = (json_input['client_id'], json_input['value'], json_input['expires'], json_input['note'],
                           self.admin.id)
        if self.context.application_database.insert_client_rent(processed_input) is False:
            self.log_user('Fail to create!')
            self.send('create_rent', 'fail')
        else:
            self.log_user('Created rent!')
            self.send('create_rent', 'ok')

    def command_get_rent(self, json_input):
        self.log_user('Requesting rent.')
        processed_input = (json_input['client_id'], json_input['note'])
        self.send('get_rent', self.context.application_database.get_client_rent(processed_input))

    def command_start_rent(self, json_input):
        self.log_user('Starting rent...')
        if self.context.application_rent.start_rent(json_input['rent_id'], self.admin.id) is False:
            self.log_user('Fail to start!')
            self.send('start_rent', 'fail')
        else:
            self.log_user('Rent started!')
            self.send('start_rent', 'ok')

    def command_stop_rent(self, json_input):
        self.log_user('Stopping rent...')
        if self.context.application_rent.stop_rent(json_input['rent_id'], self.admin.id) is False:
            self.log_user('Fail to stop!')
            self.send('stop_rent', 'fail')
        else:
            self.log_user('Rent stopped!')
            self.send('stop_rent', 'ok')

    def command_void_rent(self, json_input):
        self.log_user('Voidding rent...')
        if self.context.application_rent.void_rent(json_input['rent_id'], self.admin.id) is False:
            self.log_user('Fail to void!')
            self.send('void_rent', 'fail')
        else:
            self.log_user('Rent voided!')
            self.send('void_rent', 'ok')

    def command_get_rent_summary(self, json_input):
        self.log_user('Requesting rent summary.')
        processed_input = (json_input['from'], json_input['to'])
        self.send('get_rent_summary', self.context.application_database.get_rent_summary(processed_input))

    # Rent history
    def command_get_history_summary(self, json_input):
        self.log_user('Requesting history summary.')
        processed_input = (json_input['from'], json_input['to'])
        self.send('get_history_summary', self.context.application_database.get_history_summary(processed_input))

    # Admin
    def command_get_admin(self):
        self.log_user('Requesting Admin list.')
        output = list()
        for a in self.context.service_list:
            output.insert(0, a.admin.username)
        self.send('get_admin', tuple(output))

    def handle_command(self, json_input):
        json_command = json_input['command']
        if json_command == 'login':
            self.command_login(json_input)
            return
        if self.verify() is False:
            return
        elif json_command == 'add_client':
            self.command_add_client(json_input)
        elif json_command == 'get_client':
            self.command_get_client(json_input)
        elif json_command == 'edit_client':
            self.command_edit_client(json_input)
        elif json_command == 'create_rent':
            self.command_create_rent(json_input)
        elif json_command == 'get_rent':
            self.command_get_rent(json_input)
        elif json_command == 'start_rent':
            self.command_start_rent(json_input)
        elif json_command == 'stop_rent':
            self.command_stop_rent(json_input)
        elif json_command == 'void_rent':
            self.command_void_rent(json_input)
        elif json_command == 'get_history_summary':
            self.command_get_history_summary(json_input)
        elif json_command == 'get_rent_summary':
            self.command_get_rent_summary(json_input)
        elif json_command == 'get_admin':
            self.command_get_admin()
        else:
            self.log_user('Unidentified command - '+json_command)
