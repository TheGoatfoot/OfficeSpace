import threading
from officespaceserverservice import ServerService
from autobahn.twisted.websocket import WebSocketServerFactory, WebSocketServerProtocol, listenWS
from twisted.internet import reactor, ssl
from twisted.web.static import File
from twisted.web.server import Site


class Server:
    thread_websocket = None
    thread_alert = None
    loop = None
    stop_code = None
    context = None

    class ServiceProtocol(WebSocketServerProtocol):
        def onConnect(self, request):
            ServerService().on_connect(Server.context, request)

        def onOpen(self):
            ServerService().on_open(Server.context)

        def onMessage(self, payload, is_binary):
            ServerService().on_message(Server.context, payload, is_binary)

        def onClose(self, was_clean, code, reason):
            ServerService().on_close(Server.context, was_clean, code, reason)

    def __init__(self, context):
        self.context = context

    def start(self):
        self.thread_websocket = threading.Thread(target=self.websocket, kwargs={'context': self.context})
        self.thread_websocket.daemon = True
        self.thread_websocket.start()
        self.thread_alert = threading.Timer(10.0, self.alert, kwargs={'context': self.context})
        self.thread_alert.start()

    def stop(self):
        self.thread_alert.cancel()
        reactor.stop()

    def websocket(self, context, host='127.0.0.1', port=9000):
        ServerService.context = context
        context_factory = ssl.DefaultOpenSSLContextFactory('cert/key.key',
                                                           'cert/certificate.crt')
        factory = WebSocketServerFactory(u'wss://'+host+':'+str(port))
        factory.protocol = ServerService
        listenWS(factory, context_factory)

        reactor.run(installSignalHandlers=False)

    def alert(self, context):
        for a in context.service_list:
            a.send('alert', context.application_database.get_rent_alert())
            a.send('alert_overdue', context.application_database.get_rent_alert_overdue())
        self.thread_alert = threading.Timer(10.0, self.alert, kwargs={'context': context})
        self.thread_alert.start()

