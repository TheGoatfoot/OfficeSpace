from OpenSSL import crypto
from os.path import exists


class Certificate:
    def create_certificate(self, context):
        context.log_application.info('Creating certificate...')
        print('Creating Certificate...')
        private_key = crypto.PKey()
        private_key.generate_key(crypto.TYPE_RSA, 2048)
        certificate = crypto.X509()
        try:
            certificate.get_subject().C = input('Country(US, CN, ID) : ')
            certificate.get_subject().ST = input('State(Wyoming, Wisconsin, Jakarta Selatan) : ')
            certificate.get_subject().O = input('Organization : ')
            certificate.get_subject().OU = input('Organizational Unit(Marketing, Finance) : ')
            certificate.get_subject().C = 'OS'
        except crypto.Error:
            print('Please follow the format!')
            context.log_application.info('Certificate creation error!')
            return
        certificate.set_serial_number(1000)
        certificate.gmtime_adj_notBefore(0)
        certificate.gmtime_adj_notAfter(50 * 365 * 24 * 60 * 60)
        certificate.set_issuer(certificate.get_subject())
        certificate.set_pubkey(private_key)
        certificate.sign(private_key, 'sha1')
        open('cert/certificate.crt', "wb").write(
            crypto.dump_certificate(crypto.FILETYPE_PEM, certificate))
        open('cert/key.key', "wb").write(
            crypto.dump_privatekey(crypto.FILETYPE_PEM, private_key))
        context.log_application.info('Certificate created!')

    def is_certificate_exist(self):
        return exists('cert/certificate.crt')

    def is_key_exist(self):
        return exists('cert/key.key')
