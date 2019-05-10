from officespacedrm import DRM
from officespacecontext import Context
from officespacecommand import Command
from officespacecertificate import Certificate


import os

# Initialize
#   Context
application_context = Context()

# Start
#   Header
application_context.log_application.info('Application started! Session:'+application_context.session)
print('OfficeSpace v.' + str(application_context.application_info.get('application_version_major')) + '.' +
      str(application_context.application_info.get('application_version_minor')) + '.' +
      str(application_context.application_info.get('application_version_revision')))
print('UID : ' + application_context.application_drm.get_uid())
#   Warnings
if application_context.application_database.is_admin_empty():
    print('There is no admin, please create some using the \'admin add\' command.')
#   Certificate
while Certificate().is_certificate_exist() is False or Certificate().is_key_exist() is False:
    Certificate().create_certificate(application_context)
#   Websocket
application_context.start_server()

#   Main loop
while application_context.application_active:
    # DRM check
    if Command().main_check(application_context) is False:
        continue
    # Input
    Command().handle_command(input('>'), application_context)

# End
application_context.stop_server()
application_context.log_application.info('Application stopped')