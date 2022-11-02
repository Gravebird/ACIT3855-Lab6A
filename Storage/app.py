import swagger_ui_bundle
import connexion
import yaml
import logging, logging.config
import json
from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread
from connexion import NoContent

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.base import Base
from models.daily_sales import DailySales
from models.delivery import Delivery
import datetime

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())
    db_info = app_config['datastore']

DB_ENGINE = create_engine(f'mysql+pymysql://{db_info["user"]}:{db_info["password"]}@{db_info["hostname"]}:{db_info["port"]}/{db_info["db"]}')
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)


def get_daily_sales(timestamp):
    """ Gets new daily sales after the timestamp """
    session = DB_SESSION()

    if timestamp == 'None':
        daily_sales = session.query(DailySales)
        # change timestamp variable so logger message is more helpful
        timestamp = 'the beginning of time'
    else:
        timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
        daily_sales = session.query(DailySales).filter(DailySales.inventory_datetime >= timestamp_datetime)

    results_list = []

    for ds in daily_sales.all():
        results_list.append(ds.to_dict())
    
    session.close()

    logger.info(f'Query for Daily Sales after {timestamp} returns {len(results_list)} results')

    return results_list, 200


def get_deliveries(timestamp):
    """ Gets new deliveries after the timestamp """
    session = DB_SESSION()
    print(timestamp, type(timestamp))
    if timestamp == 'None':
        deliveries = session.query(Delivery)
        # change timestamp variable so logger message is more helpful
        timestamp = 'the beginning of time'
    else:
        timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
        deliveries = session.query(Delivery).filter(Delivery.delivery_datetime >= timestamp_datetime)

    results_list = []

    for dv in deliveries.all():
        results_list.append(dv.to_dict())

    session.close()

    logger.info(f'Query for Delivery after {timestamp} returns {len(results_list)} results')

    return results_list, 200


def process_messages():
    """ Process event messages """
    hostname = "%s:%d" % (app_config['events']['hostname'],
                          app_config['events']['port'])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config['events']['topic'])]

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

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')


if __name__ == "__main__":
    t1 = Thread(target=process_messages)
    t1.setDaemon(True)
    t1.start()
    app.run(port=8090)