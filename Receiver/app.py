import swagger_ui_bundle
import connexion
import yaml
import logging, logging.config
import datetime
import json
from pykafka import KafkaClient
from random import randint
from connexion import NoContent
import os

import requests
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


def upload_sales(body):
    """ 
        uploads items sold from the previous day and splits it into parts. 
        These parts are stored to track how much of each component was sold that day. 
    """
    trace_id = randint(10000,99999)
    logger.info(f'Received event "upload_sales" request with a trace id of {trace_id}')
    
    json_payload = {
        'restaurant_id' : body["restaurant_id"],
        'inventory_datetime' : body["inventory_datetime"],
        'cheeseburgers_sold' : body["cheeseburgers_sold"],
        'hamburgers_sold' : body["hamburgers_sold"],
        'fry_servings_sold' : body["fry_servings_sold"],
        'trace_id' : trace_id
        }

    client = KafkaClient(hosts=f'{KAFKA_HOST}:{KAFKA_PORT}')
    topic = client.topics[str.encode(KAFKA_TOPIC)]
    producer = topic.get_sync_producer()
    msg = {
        "type": "daily_sales",
        "datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "payload": json_payload
    }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    #x = requests.post(SALES_URL, json=json_payload)
    
    logger.info(f'Returned event "upload_sales" response (Id: {trace_id}) with status 201')

    return NoContent, 201


def upload_delivery(body):
    """
        uploads items received from a delivery. These items received are parts 
        of a food item, not an entire cheeseburger for example.
    """
    trace_id = randint(10000,99999)
    logger.info(f'Received event "upload_delivery" request with a trace id of {trace_id}')

    json_payload = {
        'restaurant_id' : body["restaurant_id"],
        'delivery_id' : body["delivery_id"],
        'bun_trays_received' : body["bun_trays_received"],
        'cheese_boxes_received' : body["cheese_boxes_received"],
        'fry_boxes_received' : body["fry_boxes_received"],
        'patty_boxes_received' : body["patty_boxes_received"],
        'trace_id' : trace_id
    }

    producer = topic.get_sync_producer()
    msg = {
        "type": "delivery",
        "datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "payload": json_payload
    }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    #x = requests.post(DELIVERY_URL, json=json_payload)
    
    logger.info(f'Returned event "upload_delivery" response (Id: {trace_id}) with status 201')
    
    return NoContent, 201







app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("receiver_api.yaml",
            strict_validation=True,
            validate_responses=True)

SALES_URL = app_config['eventstore1']['url']
DELIVERY_URL = app_config['eventstore2']['url']
KAFKA_HOST = app_config['events']['hostname']
KAFKA_PORT = app_config['events']['port']
KAFKA_TOPIC = app_config['events']['topic']
kafka_max_connection_retries = app_config['events']['max_retries']
kafka_sleep_time_before_reconnect = app_config['events']['kafka_sleep_time_before_reconnect']
logger.debug(f'Kafka host: {KAFKA_HOST}')
current_retry_count = 0
while current_retry_count < kafka_max_connection_retries:
    logger.info(f'Attempting to connect to kafak - Attempt #{current_retry_count}')
    try:
        client = KafkaClient(hosts=KAFKA_HOST)
        topic = client.topics[str.encode(KAFKA_TOPIC)]
        logger.info(f'Connection Attempt #{current_retry_count} successful')
        break
    except:
        logger.error(f'Kafka connection failed. Attempt #{current_retry_count}')
        time.sleep(kafka_sleep_time_before_reconnect)
        current_retry_count += 1

if __name__ == "__main__":
    app.run(port=8080)