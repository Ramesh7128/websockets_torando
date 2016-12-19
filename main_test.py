import os
import tornado.ioloop
import tornado.web
import tornado.websocket
import pika
from threading import Thread
import logging
logging.basicConfig(level=logging.INFO)


clients = []

connection = pika.BlockingConnection()
logging.info('Connected:localhost')
channel = connection.channel()

def threaded_rmq():
    channel.queue_declare(queue="my_queue")
    logging.info('consumer ready, on Hello queue')
    channel.basic_consume(consumer_callback, queue="hello", no_ack=True) 
    channel.start_consuming()
    

def disconnect_to_rabbitmq():
    channel.stop_consuming()
    connection.close()
    logging.info('Disconnected from Rabbitmq')

    
def consumer_callback(ch, method, properties, body):
        logging.info("[x] Received %r" % (body,))
        # The messagge is brodcast to the connected clients
        for itm in clients:
            itm.write_message(body)

class WSHandler(tornado.websocket.WebSocketHandler):
    def open(self,name):
        logging.info('WebSocket opened')
        self.id = name
        clients.append(self)

    def on_message(self, message):
        print 'message received:  %s' % message
        # Reverse Message and send it back
        print 'sending back message: %s' % message[::-1]
        self.write_message(message)
    
    def on_close(self):
        logging.info('WebSocket closed')
        clients.remove(self)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")
    

application = tornado.web.Application([
    (r'/ws/(.*)', WSHandler),
    (r"/", MainHandler),
])

def startTornado():
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()

def stopTornado():
    tornado.ioloop.IOLoop.instance().stop()

if __name__ == "__main__":
    logging.info('Starting thread RabbitMQ')
    threadRMQ = Thread(target=threaded_rmq)
    threadRMQ.start()

    logging.info('Starting thread Tornado')

    threadTornado = Thread(target=startTornado)
    threadTornado.start()
    try:
        raw_input("Server ready. Press enter to stop\n")
    except SyntaxError:
        pass
    try:
        logging.info('Disconnecting from RabbitMQ..')
        disconnect_to_rabbitmq()
    except Exception, e:
        pass
    stopTornado(); 
    
    logging.info('See you...')