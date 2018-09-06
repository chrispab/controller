
import logging
import time
import random
logger = logging.getLogger(__name__)
import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import socket


class WSHandler(tornado.websocket.WebSocketHandler):
    clients=[]

    def open(self):
        logger.warning("1111111  WebSocket opened from web to server")
        if self not in self.clients:
            self.clients.append(self)
            logger.warning("1111111  appending socket to list")
            self.write_message("you've been connected. Congratz.")

    def on_message(self, message):
        logger.warning('000000000<message received>:  %s' % message)
        self.write_message(message[::-1])

    def on_close(self):
        print('connection closed')
        logger.warning("22222222222222 WebSocket Closed from web on server")
        #if self in cls.clients:
         #   clients.remove(self)

    def check_origin(self, origin):
        return True

    @classmethod
    def send_message(cls, message):
        #global clients
        logger.warning('33333333333333333 TRYING TO SEND A WS MESSAGE:  %s' % message)
        logger.warning('444444444===WS SELF : %s' % cls.clients)
        for ws in cls.clients:
            logger.warning('55555555555==WS OBJ:  %s' % ws.print())
            ws.write_message(message)


def pre_send_message(message):
    #global clients
    logger.warning('33333333333333333 PRE SEND:  %s' % message)
    # logger.warning('444444444===WS SELF : %s' % cls.clients)
    # for ws in cls.clients:
    #     logger.warning('55555555555==WS OBJ:  %s' % ws.print())
    #     ws.write_message(message)

    server = tornado.ioloop.IOLoop.current()
    data = "whatever"
    server.add_callback(WSHandler.send_message, data)


application = tornado.web.Application([
    (r'/ws', WSHandler),
])

def createTornado():
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8888)
    myIP = socket.gethostbyname(socket.gethostname())
#    print('*** Websocket Server Started at %s***' % myIP)
    logger.warning('*** Websocket Server Started at %s***' % myIP)
    logger.warning("++++++++++++++ I'm a websocket process - Hi! MAIN ++++++++++++")
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8888)
    myIP = socket.gethostbyname(socket.gethostname())
    print('*** Websocket Server Started at %s***' % myIP)
    logger.warning("++++++++++++++ I'm a websocket process - Hi! ++++++++++++")
    tornado.ioloop.IOLoop.instance().start()
