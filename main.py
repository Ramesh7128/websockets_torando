import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import socket
import os

# import tornado.template

'''
simple Websocket Echo server that uses the Tornado websocket handler.
''' 


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')


class WSHandler(tornado.websocket.WebSocketHandler):
    # client = []

    def open(self):
        # WSHandler.clients.append(self)
        print 'new connection'
      
    def on_message(self, message):
        print 'message received:  %s' % message
        # Reverse Message and send it back
        print 'sending back message: %s' % message[::-1]
        self.write_message('%s' % message[::-1])
        from time import sleep
        sleep(5)
        self.write_message('test')
        
 
    def on_close(self):
        print 'connection closed'
 
    def check_origin(self, origin):
        return True
 
application = tornado.web.Application([
    (r'/', MainHandler),
    (r'/ws', WSHandler),
])
 
 
if __name__ == "__main__":
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8888)
    myIP = socket.gethostbyname(socket.gethostname())
    print '*** Websocket Server Started at %s***' % myIP
    tornado.ioloop.IOLoop.instance().start()