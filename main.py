import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import socket
import os

# pika
import pika
import tornado
import tornado.websocket as websocket
from pika.adapters.tornado_connection import TornadoConnection

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
        self.application.pc.add_event_listener(self)
        print 'new connection'
      
    def on_message(self, message):
        print 'message received:  %s' % message
        # Reverse Message and send it back
        print 'sending back message: %s' % message[::-1]
        
        
        # pika sending message
        import pika
        connection = pika.BlockingConnection(pika.ConnectionParameters(
                       'localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='hello')
        channel.basic_publish(exchange='',
                              routing_key='hello',
                              body=message)
        print 'Hello World!'
        connection.close()

        # self.write_message('%s' % message[::-1])

        self.write_message('test')
        
    
    def pika_push_message(self, message):
        """function to push messages to clients when a call gets made from the pika"""
        print 'message from pika: %s' % message
        self.write_message('%s' % message)

    
    def on_close(self):
        self.application.pc.remove_event_listener(self)
        print 'connection closed'
 
    def check_origin(self, origin):
        return True


    
class PikaClient(object):
 
    def __init__(self, io_loop):
        print 'PikaClient: __init__'
        self.io_loop = io_loop
 
        self.connected = False
        self.connecting = False
        self.connection = None
        self.channel = None
 
        self.event_listeners = set([])
 
    def connect(self):
        if self.connecting:
            print 'PikaClient: Already connecting to RabbitMQ'
            return
 
        print 'PikaClient: Connecting to RabbitMQ'
        self.connecting = True
 
        cred = pika.PlainCredentials('guest', 'guest')
        param = pika.ConnectionParameters(
            host='localhost',
            port=5672,
            virtual_host='/',
            credentials=cred
        )
 
        self.connection = TornadoConnection(param,
            on_open_callback=self.on_connected)
        self.connection.add_on_close_callback(self.on_closed)
 
    def on_connected(self, connection):
        print 'PikaClient: connected to RabbitMQ'
        self.connected = True
        self.connection = connection
        self.connection.channel(self.on_channel_open)
 
    def on_channel_open(self, channel):
        # pika.log.info('PikaClient: Channel open, Declaring exchange')
        self.channel = channel
        self.channel.queue_declare(queue='hello')
        # declare exchanges, which in turn, declare
        # queues, and bind exchange to queues
 
    def on_closed(self, connection):
        # pika.log.info('PikaClient: rabbit connection closed')
        self.io_loop.stop()
 
    def on_message(self, channel, method, header, body):
        # pika.log.info('PikaClient: message received: %s' % body)
        print "on message"
        self.notify_listeners(event_factory(body))
 
    def notify_listeners(self, event_obj):
        # here we assume the message the sourcing app
        # post to the message queue is in JSON format
        event_json = json.dumps(event_obj)
 
        for listener in self.event_listeners:
            listener.write_message(event_json)
            # pika.log.info('PikaClient: notified %s' % repr(listener))
 
    def add_event_listener(self, listener):
        self.event_listeners.add(listener)
        # pika.log.info('PikaClient: listener %s added' % repr(listener))
 
    def remove_event_listener(self, listener):
        try:
            self.event_listeners.remove(listener)
            # pika.log.info('PikaClient: listener %s removed' % repr(listener))
        except KeyError:
            pass
 
application = tornado.web.Application([
    (r'/', MainHandler),
    (r'/ws', WSHandler),
])
 
 
if __name__ == "__main__":
    # http_server = tornado.httpserver.HTTPServer(application)
    # http_server.listen(8888)
    # myIP = socket.gethostbyname(socket.gethostname())
    # print '*** Websocket Server Started at %s***' % myIP
    # tornado.ioloop.IOLoop.instance().start()

    # pika.log.setup(color=True)
    io_loop = tornado.ioloop.IOLoop.instance()
    # PikaClient is our rabbitmq consumer
    pc = PikaClient(io_loop)
    application.pc = pc
    application.pc.connect()
 
    application.listen(8888)
    io_loop.start()