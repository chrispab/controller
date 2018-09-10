
import logging
import time
import random
logger = logging.getLogger(__name__)
import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import socket
from tornado import ioloop, web, websocket

class TestHandler(tornado.web.RequestHandler):
    def get(self):
        server = ioloop.IOLoop.current()
        data = "testhandler 155 whatever"
        server.add_callback(WSHandler.send_message, data)
        self.set_status(200)
        self.finish()

class WSHandler(tornado.websocket.WebSocketHandler):
    clients=[]

    def open(self):
        logger.warning("AAAAAAAAAA  WebSocket opened from web to server")
        self.set_nodelay(True)

        #if self not in self.clients:
        #logger.warning("CCCCCCCCCC  appending socket to list")
        self.clients.append(self)

        for ws in self.clients:
            logger.warning('BBBBBBBBBBB a ws item ==WS OBJ:  %s' % ws)
            #ws.write_message(message)

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
        logger.warning('XXXXXXXXXX TRYING TO SEND A WS MESSAGE:  %s' % message)
        logger.warning('YYYYYYYYYY WS SELF - CLIENTS : %s' % cls.clients)
        for ws in cls.clients:
            logger.warning('ZZZZZZZZZZ WS OBJ:  %s' % ws)
            ws.write_message(message)

        #cls.finish()
    # @classmethod
    # def send_message(cls, message):
    #     removable = set()
    #     for ws in cls.live_web_sockets:
    #         if not ws.ws_connection or not ws.ws_connection.stream.socket:
    #             removable.add(ws)
    #         else:
    #             ws.write_message(message)
    #     for ws in removable:
    #         cls.live_web_sockets.remove(ws)



def pre_send_message(message):
    #global clients
    logger.warning('PPPPPPPPPPPP PRE SEND message:  %s' % message)
    server = tornado.ioloop.IOLoop.current()
    logger.warning('PPPPPPPPPPPP PRE SEND server:  %s' % server)
    data = "PPPPP whatever"
#        retval = tornado.ioloop.IOLoop.current().add_callback(WSHandler.send_message, data)
        #tornado.ioloop.IOLoop.current().add_callback(WSHandler.send_message, data)
   # server.add_callback(WSHandler.send_message, data)
        #retval = tornado.ioloop.IOLoop.current().add_callback(WSHandler.send_message, data)
        #retval = server.add_callback(WSHandler.send_message, data)
        #logger.warning('PPPPPPPPPP RETVAL PRE SEND:  %s' % retval)
    handle.add_callback(WSHandler.send_message, data)
    #ioloop.IOLoop.current().add_callback().
    #ioloop.IOLoop.current().fi
    # addHandler=TestHandler
    # addHandler.get()
    # newCallBack=TestHandler()
    # newCallBack.get()
    #TestHandler.get()



application = tornado.web.Application([
    (r'/ws', WSHandler),
    (r"/test/", TestHandler),
])

handle = tornado.ioloop.IOLoop.current()

def createTornado():
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8888)
    myIP = socket.gethostbyname(socket.gethostname())
#    print('*** Websocket Server Started at %s***' % myIP)
    logger.warning('*** Websocket Server Started at %s***' % myIP)
    logger.warning("++++++++++++++ I'm a websocket process - Hi! MAIN ++++++++++++")

    # server = tornado.ioloop.IOLoop.current()
    data = "whatever"
    # retval = server.add_callback(WSHandler.send_message, data)
    retval = tornado.ioloop.IOLoop.current().add_callback(WSHandler.send_message, data)
    logger.warning('qqqqqqqqqqqqqqqqqq PRE SEND:  %s' % retval)

    tornado.ioloop.IOLoop.current().start()

if __name__ == "__main__":
    createTornado()
