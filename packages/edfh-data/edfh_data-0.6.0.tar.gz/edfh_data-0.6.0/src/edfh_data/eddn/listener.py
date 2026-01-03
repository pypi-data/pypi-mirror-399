import os
from pathlib import Path
import sys
import time
import zlib

import orjson
import pika
import zmq


def run():

    if Path(".env").is_file():
        from dotenv import load_dotenv

        load_dotenv()

    EDDN_RELAY_URL = "tcp://eddn.edcd.io:9500"
    EDDN_SOCKET_TIMEOUT = 600000
    RMQ_EXCHANGE_NAME = "eddn_raw"

    context = zmq.Context()
    subscriber = context.socket(zmq.SUB)

    subscriber.setsockopt(zmq.SUBSCRIBE, b"")
    subscriber.setsockopt(zmq.RCVTIMEO, EDDN_SOCKET_TIMEOUT)

    rmq_credentials = pika.PlainCredentials(
        username=os.getenv("RMQ_USER", "guest"),
        password=os.getenv("RMQ_PASSWD", "guest"),
    )
    rmq_connect_params = pika.ConnectionParameters(
        host=os.getenv("RMQ_HOST", "localhost"),
        credentials=rmq_credentials,
        heartbeat=20,
    )

    while True:
        try:
            subscriber.connect(EDDN_RELAY_URL)

            rmq_connection = None
            rmq_connection = pika.BlockingConnection(rmq_connect_params)
            rmq_channel = rmq_connection.channel()
            rmq_channel.exchange_declare(
                exchange=RMQ_EXCHANGE_NAME, exchange_type="fanout"
            )

            while True:
                try:
                    event_raw = subscriber.recv()

                    if event_raw is False:
                        subscriber.disconnect(EDDN_RELAY_URL)
                        break

                    rmq_channel.basic_publish(
                        exchange=RMQ_EXCHANGE_NAME,
                        routing_key="",
                        body=event_raw,
                        properties=pika.BasicProperties(
                            delivery_mode=pika.DeliveryMode.Persistent
                        ),
                    )

                    event_json = zlib.decompress(event_raw)
                    event = orjson.loads(event_json)
                    print(f" [x] Published {event.get("$schemaRef")}")

                except KeyError as e:
                    print(e)

        except KeyboardInterrupt:
            subscriber.disconnect(EDDN_RELAY_URL)
            rmq_connection.close()
            sys.exit()

        except Exception as e:
            print(repr(e))
            try:
                subscriber.disconnect(EDDN_RELAY_URL)
            except Exception:
                pass

            try:
                if rmq_connection and rmq_connection.is_open:
                    rmq_connection.close()
            except Exception:
                pass

            time.sleep(5)


if __name__ == "__main__":
    run()
