import signal
import json
import time
from os import getenv

import pika
from escpos.printer import Usb
from printer import print_receipt


QUEUE_NAME = getenv("PRINTER_ROLE", "both")

def on_message_factory(receipt_type):
    def on_message(channel, method, properties, body):
        try:
            data = json.loads(body.decode())
            print_receipt(printer, data)
            if receipt_type == "both":
                time.sleep(int(getenv("SLEEP", 5)))
            channel.basic_ack(delivery_tag=method.delivery_tag)
        except Exception:
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    return on_message

def shutdown(sig, frame):
    print("Shutting down...")
    channel.stop_consuming()

connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host=getenv("QUEUE_HOST", "localhost"),
        credentials=pika.PlainCredentials(
            username=getenv("QUEUE_USER", "admin"),
            password=getenv("QUEUE_PASS", "rabbitmqpassword")
        )
    )
)

global printer

printer = Usb(
    idVendor=8401,
    idProduct=28679,
    in_ep=0x82,
    out_ep=0x02
)

channel = connection.channel()

channel.exchange_declare(
    exchange="receipts",
    exchange_type="direct",
    durable=True
)

channel.queue_declare(queue="queue.client", durable=True)
channel.queue_bind(
    queue="queue.client",
    exchange="receipts",
    routing_key="receipt.client"
)

channel.queue_declare(queue="queue.kitchen", durable=True)
channel.queue_bind(
    queue="queue.kitchen",
    exchange="receipts",
    routing_key="receipt.kitchen"
)

def print_both(channel):
    while True:
        client_method, client_props, client_body = channel.basic_get("queue.client", auto_ack=False)
        kitchen_method, kitchen_props, kitchen_body = channel.basic_get("queue.kitchen", auto_ack=False)

        if client_body and kitchen_body:
            try:
                print_receipt(printer, json.loads(client_body.decode()))
                time.sleep(int(getenv("SLEEP", 5)))
                print_receipt(printer, json.loads(kitchen_body.decode()))
                channel.basic_ack(delivery_tag=client_method.delivery_tag)
                channel.basic_ack(delivery_tag=kitchen_method.delivery_tag)
            except Exception:
                channel.basic_nack(delivery_tag=client_method.delivery_tag, requeue=False)
                channel.basic_nack(delivery_tag=kitchen_method.delivery_tag, requeue=False)
        else:
            if client_body:
                channel.basic_nack(delivery_tag=client_method.delivery_tag, requeue=True)
            if kitchen_body:
                channel.basic_nack(delivery_tag=kitchen_method.delivery_tag, requeue=True)
            time.sleep(1)

signal.signal(signal.SIGTERM, shutdown)
signal.signal(signal.SIGINT, shutdown)

if QUEUE_NAME == "both":
    print_both(channel)
else:
    channel.basic_consume(
        queue=f"queue.{QUEUE_NAME}",
        on_message_callback=on_message_factory(QUEUE_NAME)
    )
    channel.start_consuming()

connection.close()
