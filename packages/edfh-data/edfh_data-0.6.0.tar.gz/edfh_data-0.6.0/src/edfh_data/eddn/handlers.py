import datetime as dt
import os
from typing import Mapping
import zlib

import orjson
import pika
from sqlalchemy.exc import OperationalError

from edfh_data.db.crud import create_update_station
from edfh_data.db.crud import create_update_station_market
from edfh_data.db.crud import create_update_system
from edfh_data.db.utils import init_db
from edfh_data.exceptions import EventTooOldError
from edfh_data.models import construction_station_types
from edfh_data.models import Station
from edfh_data.models import StationMarket
from edfh_data.models import System

JOURNAL_V1_SCHEMA = "https://eddn.edcd.io/schemas/journal/1"
COMMODITY_V3_SCHEMA = "https://eddn.edcd.io/schemas/commodity/3"


def handle_journal_v1_fsdjump(message: Mapping) -> None:
    """Handle the journal/1 messages with event==FSDJump."""

    system = System(**message)

    create_update_system(system)


def handle_journal_v1_docked(message: Mapping) -> None:
    """Handle the journal/1 message with event==Docked."""
    # Ignore colonisation ships & construction sites
    if (
        message["StationType"] in construction_station_types
        or "colonisationship" in message["StationName"].lower()
    ):
        return

    station = Station(**message)

    create_update_station(station)


def handle_commodity_v3(message: Mapping) -> None:
    """Handle the commodity/3 message."""

    market = StationMarket(**message)

    create_update_station_market(market)
    pass


def handle_eddn_event(
    event: dict, max_age: dt.timedelta = dt.timedelta(hours=1)
) -> bool:
    """Handle any eddn event."""
    handled = False
    message = event["message"]

    now = dt.datetime.now(tz=dt.timezone.utc)
    message_datetime = dt.datetime.fromisoformat(message["timestamp"]).replace(
        tzinfo=dt.timezone.utc
    )
    messag_age = now - message_datetime

    if messag_age > max_age:
        raise EventTooOldError(
            f"The event timestamp is too old: {message['timestamp']}"
        )

    if event["$schemaRef"] == JOURNAL_V1_SCHEMA and message.get("event") == "FSDJump":
        handle_journal_v1_fsdjump(message)
        handled = True

    elif event["$schemaRef"] == JOURNAL_V1_SCHEMA and message.get("event") == "Docked":
        handle_journal_v1_docked(message)
        handled = True

    elif event["$schemaRef"] == COMMODITY_V3_SCHEMA:
        handle_commodity_v3(message)
        handled = True

    return handled


def run():

    init_db()

    RMQ_EXCHANGE_NAME = "eddn_raw"
    RMQ_QUEUE_NAME = "eddn_raw_queue"

    rmq_connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=os.getenv("RMQ_HOST", "localhost"),
            credentials=pika.PlainCredentials(
                username=os.getenv("RMQ_USER", "guest"),
                password=os.getenv("RMQ_PASSWD", "guest"),
            ),
        )
    )

    rmq_channel = rmq_connection.channel()
    rmq_channel.exchange_declare(exchange=RMQ_EXCHANGE_NAME, exchange_type="fanout")

    rmq_channel.queue_declare(queue=RMQ_QUEUE_NAME, durable=True)
    rmq_channel.queue_bind(exchange=RMQ_EXCHANGE_NAME, queue=RMQ_QUEUE_NAME)

    def callback(ch, method, properties, body):
        try:
            event_json = zlib.decompress(body)
            event = orjson.loads(event_json)
            print(f" [x] Received {event["$schemaRef"]}")

            handle_eddn_event(event, max_age=dt.timedelta(days=7))

            ch.basic_ack(delivery_tag=method.delivery_tag)

        except OperationalError as e:
            if e.orig and e.orig.args[0] == 1020:
                # OperationalError(1020, "Record has changed since last read in
                # table 'systems'")
                # Do not aknowledge and requeue for re-processing
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            else:
                ch.basic_ack(delivery_tag=method.delivery_tag)
                print(e)

        except Exception as e:
            ch.basic_ack(delivery_tag=method.delivery_tag)
            print(e)

    rmq_channel.basic_qos(prefetch_count=int(os.getenv("RMQ_HANDLER_PREFETCH", 1)))
    rmq_channel.basic_consume(queue=RMQ_QUEUE_NAME, on_message_callback=callback)

    try:
        rmq_channel.start_consuming()
    except KeyboardInterrupt:
        rmq_channel.stop_consuming()

    rmq_connection.close()


if __name__ == "__main__":
    run()
