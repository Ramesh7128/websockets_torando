import pika
from main import WSHandler
import tornado.websocket


connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='localhost'))
channel = connection.channel()

web_soc_handler = WSHandler(tornado.websocket.WebSocketHandler)

channel.queue_declare(queue='hello')

def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)
    # new_body = "returned from pika: %s" % body
    # web_soc_handler.pika_push_message(new_body)

channel.basic_consume(callback,
                      queue='hello',
                      no_ack=True)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()