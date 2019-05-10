import getpass

from officespacedrm import DRM
from officespaceadminutility import AdminUtility


class Command:
    def main_check(self, context):
        if context.application_drm_check is False:
            DRM().handle_checks(context)
            return False
        return True

    def command_help(self, page):
        print()

    # Admin Related Stuff
    def command_admin(self, context):
        username = input('username: ')
        password = getpass.getpass('password: ')
        context.application_database.insert_admin(username, password)
        context.application_database.database.commit()
        context.log_application.info("Created new admin '" + username + "'.")

    def command_admin_verify(self, context):
        username = input('username: ')
        alleged_password = getpass.getpass('password: ')
        print(AdminUtility().verify(context, username, alleged_password))

    def command_admin_broadcast(self, context):
        for a in context.service_list:
            a.service.sendMessage(bytes('Hello', 'utf-8'))

    def command_service_list(self, context):
        for a in context.service_list:
            print(a.admin.username+' - '+a.peer)

    def command_error(self, inp, context):
        context.log_application.info("Invalid command '" + inp + "'.")
        print("Unknown command '" + inp + "'.")

    def handle_command(self, inp, context):
        commands = inp.split(' ')
        for i in range(len(commands), 16):
            commands += ('', )
        context.log_application.info("Command given '" + inp + "'.")
        # Quit the application
        if commands[0] == 'quit':
            context.application_active = False
        # Print out help page
        elif commands[0] == 'help':
            if len(commands) == 1:
                self.command_help(1)
            else:
                self.command_help(commands[1])
        # Admin Stuff
        elif commands[0] == 'admin':
            if commands[1] == 'verify':
                self.command_admin_verify(context)
            elif commands[1] == 'add':
                self.command_admin(context)
            elif commands[1] == 'broadcast':
                self.command_admin_broadcast(context)
            elif commands[1] == 'list':
                self.command_service_list(context)
            else:
                self.command_error(inp, context)
        else:
            self.command_error(inp, context)
