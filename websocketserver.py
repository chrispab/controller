
import logging
import time
import random
logger = logging.getLogger(__name__)
import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import socket
'''
This is a simple Websocket Echo server that uses the Tornado websocket handler.
Please run `pip install tornado` with python of version 2.7.9 or greater to install tornado.
This program will echo back the reverse of whatever it recieves.
Messages are output to the terminal for debuggin purposes. 
'''

# clients = []

# def send_to_all_clients(message):
#     for client in clients:
#         client.write_message(message)
#         logger.warning('$$$$$$$$$$$$$$$$$$$$$  SENDING WS MESSAGE TO ALL CLIENTS $$$$$$$$$$$$$$$:  %s' % message)


class WSHandler(tornado.websocket.WebSocketHandler):

    live_web_sockets = set()
    thisSocket = tornado.websocket.WebSocketHandler

    # def open(self):
    #     print('new connection')
    #     clients.append(self)

    def open(self):
        logger.warning("1111111  WebSocket opened from web to server")
        #self.set_nodelay(True)
        self.live_web_sockets.add(self)
        self.thisSocket=self
        self.write_message("you've been connected. Congratz.")

    def on_message(self, message):
        #print('message received:  %s' % message)
        logger.warning('000000000<message received>:  %s' % message)
        
        #do what ever we need to message e.g 
        # Reverse Message and send it back to browser
        #or in this case we a feeding text from control process thru q to  websocket server , then websocket sends to browser
        # to browser page
        #print('sending back message: %s' % message[::-1])
        #self.write_message(message[::-1])

   #or in this case we a feeding text from control process thru q to this websocket server , then websocket sends to browser
    #def on

    def on_close(self):
        print('connection closed')
        logger.warning("22222222222222 WebSocket Closed from web on server")

        #clients.remove(self)

    @classmethod
    def send_message(cls, message):
        logger.warning('33333333333333333 TRYING TO SEND A WS MESSAGE:  %s' % message)
        removable = set()
        #message = ''
        logger.warning('444444444===WS SET:  %s' % cls.live_web_sockets)

        for ws in cls.live_web_sockets:
            logger.warning('55555555555==WS OBJ:  %s' % ws.print())
            # if not ws.ws_connection or not ws.ws_connection.stream.socket:
            #     removable.add(ws)
            # else:
            ws.write_message(message)
        # for ws in removable:
        #     cls.live_web_sockets.remove(ws)
        #self.write_message(message)


    def check_origin(self, origin):
        return True


application = tornado.web.Application([
    (r'/ws', WSHandler),
])

def main():
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
