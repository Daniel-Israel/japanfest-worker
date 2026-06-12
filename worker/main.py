import signal

from os import getenv

import pika

def on_message(channel, method, properties, body):
    try:
        # process and print
        channel.basic_ack(delivery_tag=method.delivery_tag)
        print(body.decode())
    except Exception:
        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

def shutdown(sig, frame):
    print("Shutting down...")
    channel.stop_consuming()  # breaks out of start_consuming()

connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host=getenv("QUEUE_HOST", "localhost"),
        credentials=pika.PlainCredentials(
            username=getenv("QUEUE_USER", "admin"),
            password=getenv("QUEUE_PASS", "rabbitmqpassword")
        )
    )
)
channel = connection.channel()

channel.exchange_declare(exchange="receipts", exchange_type="direct", durable=True)

channel.queue_declare(queue="queue.client", durable=True)
channel.queue_bind(queue="queue.client", exchange="receipts", routing_key="receipt.client")

channel.queue_declare(queue="queue.kitchen", durable=True)
channel.queue_bind(queue="queue.kitchen", exchange="receipts", routing_key="receipt.kitchen")

channel.basic_consume(queue=getenv("QUEUE_NAME", "queue.client"), on_message_callback=on_message)

signal.signal(signal.SIGTERM, shutdown)  # systemd stop / kill
signal.signal(signal.SIGINT, shutdown)   # Ctrl+C

channel.start_consuming()  # blocks here



connection.close()  # runs after stop_consuming() returns
