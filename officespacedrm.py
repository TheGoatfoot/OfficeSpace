from chaintools import ChainTools


class DRM:
    def handle_checks(self, context):
        if ChainTools().is_keyfile_exist() is False:
            # If keyfile does not exist
            # ask them to input the code
            context.log_application.error('Could not found key file!')
            input_code = input('Please input the activation code : ')
            if context.application_drm.verify_key(ChainTools().deserialize_byte(input_code)) is False:
                context.log_application.error('Invalid key!')
                print('Invalid activation code!')
            else:
                context.application_drm.create_keyfile(ChainTools().deserialize_byte(input_code))
                context.application_drm_check = True
        else:
            # if it exists check the legitimacy
            if context.application_drm.is_keyfile_legit() is False:
                context.log_application.error('Invalid key!')
                print('Invalid activation code!')
            else:
                context.application_drm_check = True
