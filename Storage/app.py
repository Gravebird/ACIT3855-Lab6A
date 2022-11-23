import swagger_ui_bundle
import connexion
import yaml
import logging, logging.config
import json
from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread
from connexion import NoContent
import os

from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
from models.base import Base
from models.daily_sales import DailySales
from models.delivery import Delivery
import datetime
import time

if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yml"
    log_conf_file = "/config/log_conf.yml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yml"
    log_conf_file = "log_conf.yml"


with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())

with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

logger.info(f'App Conf File: {app_conf_file}')
logger.info(f'Log Conf File: {log_conf_file}')

db_info = app_config['datastore']
events_info = app_config['events']

kafka_hostname = "%s:%d" % (events_info['hostname'],
                        events_info['port'])
kafka_max_connection_retries = events_info['max_retries']
kafka_topic = events_info['topic']
kafka_sleep_time_before_reconnect = events_info['kafka_sleep_time_before_reconnect']

DB_ENGINE = create_engine(f'mysql+pymysql://{db_info["user"]}:{db_info["password"]}@{db_info["hostname"]}:{db_info["port"]}/{db_info["db"]}')
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)


def get_daily_sales(start_timestamp, end_timestamp):
    """ Gets new daily sales after the timestamp """
    session = DB_SESSION()

    if start_timestamp == 'None':
        daily_sales = session.query(DailySales)
        # change timestamp variable so logger message is more helpful
        start_timestamp = 'the beginning of time'
    else:
        start_timestamp_datetime = datetime.datetime.strptime(start_timestamp, "%Y-%m-%dT%H:%M:%SZ")
        end_timestamp_datetime = datetime.datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%SZ")
        daily_sales = session.query(DailySales).filter(and_(DailySales.inventory_datetime >= start_timestamp_datetime, DailySales.inventory_datetime < end_timestamp_datetime))

    results_list = []

    for ds in daily_sales.all():
        results_list.append(ds.to_dict())
    
    session.close()

    logger.info(f'Query for Daily Sales after {start_timestamp} returns {len(results_list)} results')

    return results_list, 200


def get_deliveries(start_timestamp, end_timestamp):
    """ Gets new deliveries after the timestamp """
    session = DB_SESSION()
    print(start_timestamp, type(start_timestamp))
    if start_timestamp == 'None':
        deliveries = session.query(Delivery)
        # change timestamp variable so logger message is more helpful
        start_timestamp = 'the beginning of time'
    else:
        start_timestamp_datetime = datetime.datetime.strptime(start_timestamp, "%Y-%m-%dT%H:%M:%SZ")
        end_timestamp_datetime = datetime.datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%SZ")
        deliveries = session.query(Delivery).filter(and_(Delivery.delivery_datetime >= start_timestamp_datetime, Delivery.delivery_datetime < end_timestamp_datetime))

    results_list = []

    for dv in deliveries.all():
        results_list.append(dv.to_dict())

    session.close()

    logger.info(f'Query for Delivery after {start_timestamp} returns {len(results_list)} results')

    return results_list, 200


def process_messages():
    """ Process event messages """
    
    current_retry_count = 0
    while current_retry_count < kafka_max_connection_retries:
        logger.info(f'Attempting to connect to kafak - Attempt #{current_retry_count}')
        try:
            client = KafkaClient(hosts=kafka_hostname)
            topic = client.topics[str.encode(kafka_topic)]
            logger.info(f'Connection Attempt #{current_retry_count} successful')
            break
        except:
            logger.error(f'Kafka connection failed. Attempt #{current_retry_count}')
            time.sleep(kafka_sleep_time_before_reconnect)
            current_retry_count += 1

    # Create a consume on consumer group, that only reads new messages
    # (uncommitted messages) when the service re-starts (i.e., it doesn't
    # read all the old messages from the history in the message queue).
    consumer = topic.get_simple_consumer(consumer_group=b'event_group',
                                         reset_offset_on_start=False,
                                         auto_offset_reset=OffsetType.LATEST)

    # This is blocking - it will wait for a new message
    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        logger.info("Message: %s" % msg)

        payload = msg["payload"]

        if msg["type"] == "daily_sales":
            # Store the daily sales event (i.e., the payload) to the DB
            session = DB_SESSION()
            daily_sales = DailySales(payload['restaurant_id'], payload['cheeseburgers_sold'],
                payload['hamburgers_sold'], payload['fry_servings_sold'], payload['trace_id'])
            session.add(daily_sales)
            session.commit()
            session.close()
            logger.debug(f'Stored event "upload_sales" request with a trace id of {payload["trace_id"]}')
        
        elif msg["type"] == "delivery":
            # Store the delivery event (i.e., the payload) to the DB
            session = DB_SESSION()
            delivery = Delivery(payload['restaurant_id'], payload['delivery_id'],
                payload['bun_trays_received'], payload['cheese_boxes_received'],
                payload['fry_boxes_received'], payload['patty_boxes_received'], payload['trace_id'])
            session.add(delivery)
            session.commit()
            session.close()
            logger.debug(f'Stored event "upload_delivery" request with a trace id of {payload["trace_id"]}')
            
        # Commit the new message as being read
        consumer.commit_offsets()


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("storage_api.yaml",
            strict_validation=True,
            validate_responses=True)


if __name__ == "__main__":
    t1 = Thread(target=process_messages)
    t1.setDaemon(True)
    t1.start()
    app.run(port=8090)