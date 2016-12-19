import pika
import json

connection = pika.BlockingConnection(pika.ConnectionParameters(
               'localhost'))
channel = connection.channel()


channel.queue_declare(queue='hello')

message = json.dumps({"message": "dksbdsk", "web_socket": "ramesh", "name": "ramesh"})

channel.basic_publish(exchange='',
                      routing_key='hello',
                      body=message)
print 'Hello World!'

connection.close()
