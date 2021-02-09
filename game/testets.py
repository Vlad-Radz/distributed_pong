import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='192.168.178.43'))
channel = connection.channel()

channel.exchange_declare(exchange='moves', exchange_type='direct')

result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue

channel.queue_bind(
    exchange='moves', queue=queue_name, routing_key='hello')

print(' [*] Waiting for logs. To exit press CTRL+C')


def callback(ch, method, properties, body):
    print(" [x] %r:%r" % (method.routing_key, body))


channel.basic_consume(
    queue=queue_name, on_message_callback=callback, auto_ack=True)

channel.start_consuming()
