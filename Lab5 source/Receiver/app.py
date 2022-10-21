import swagger_ui_bundle
import connexion
import yaml
import logging, logging.config
from random import randint
from connexion import NoContent

import requests


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
    
    x = requests.post(SALES_URL, json=json_payload)
    
    logger.info(f'Returned event "upload_sales" response (Id: {trace_id}) with status {x.status_code}')

    return NoContent, x.status_code


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

    x = requests.post(DELIVERY_URL, json=json_payload)
    
    logger.info(f'Returned event "upload_delivery" response (Id: {trace_id}) with status {x.status_code}')
    
    return NoContent, x.status_code







app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("receiver_api.yaml",
            strict_validation=True,
            validate_responses=True)

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

SALES_URL = app_config['eventstore1']['url']
DELIVERY_URL = app_config['eventstore2']['url']

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)
    
logger = logging.getLogger('basicLogger')

if __name__ == "__main__":
    app.run(port=8080)