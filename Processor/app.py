import swagger_ui_bundle
import connexion
import yaml
import logging, logging.config
from connexion import NoContent
import requests
import json as js

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from apscheduler.schedulers.background import BackgroundScheduler
import datetime
from flask_cors import CORS, cross_origin

from models.base import Base
from models.stats import InventoryStats

with open('app_conf.yml', 'r') as f:
    app_conf = yaml.safe_load(f.read())

db_name = app_conf['datastore']['filename']

DB_ENGINE = create_engine(f'sqlite:///{db_name}')
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

STORAGE_URL = app_conf['eventstore']['url']

def get_stats():
    """ Gets all stats relating to daily sales and deliveries """
    logger.info("Get_stats request started")
    session = DB_SESSION()
    results = session.query(InventoryStats).order_by(InventoryStats.last_updated.desc()).first()
    
    if results == None:
        logger.error("Statistics do not exist")
        return 404
    results = results.to_dict()
    
    date_time = datetime.datetime.now()
    date_time = date_time.strftime("%Y-%m-%dT%H:%M:%SZ")

    json = {
        'num_daily_sales_events' : results['num_daily_sales_events'],
        'max_cheeseburgers_sold' : results['max_cheeseburgers_sold'],
        'max_fry_servings_sold' : results['max_fry_servings_sold'],
        'max_hamburgers_sold' : results['max_hamburgers_sold'],
        'num_delivery_events' : results['num_delivery_events'],
        'max_bun_trays_received' : results['max_bun_trays_received'],
        'max_fry_boxes_received' : results['max_fry_boxes_received'],
        'last_updated' : date_time
    }
    logger.debug(f'Contents of dictionary: {json}')
    logger.info("Get_stats request completed")

    session.close()

    return json, 200

    


def populate_stats():
    """ Periodically update stats """
    logger.info("Start Periodic Processing")

    session = DB_SESSION()
    json = {
        'num_daily_sales_events' : 0,
        'max_cheeseburgers_sold' : 0,
        'max_fry_servings_sold' : 0,
        'max_hamburgers_sold' : 0,
        'num_delivery_events' : 0,
        'max_bun_trays_received' : 0,
        'max_fry_boxes_received' : 0
    }
    results = session.query(InventoryStats).order_by(InventoryStats.last_updated.desc()).first()
    if results == None:
        date_time = None
    else:
        res_dict = results.to_dict()
        date_time = res_dict['last_updated']
        json['num_daily_sales_events'] = res_dict['num_daily_sales_events']
        json['max_cheeseburgers_sold'] = res_dict['max_cheeseburgers_sold']
        json['max_fry_servings_sold'] = res_dict['max_fry_servings_sold']
        json['max_hamburgers_sold'] = res_dict['max_hamburgers_sold']
        json['num_delivery_events'] = res_dict['num_delivery_events']
        json['max_bun_trays_received'] = res_dict['max_bun_trays_received']
        json['max_fry_boxes_received'] = res_dict['max_fry_boxes_received']

    current_timestamp = datetime.datetime.now()
    current_timestamp = current_timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")

    recent_sales_response = requests.get(f'{STORAGE_URL}/get_daily_sales?start_timestamp={date_time}&end_timestamp={current_timestamp}')
    recent_deliveries_response = requests.get(f'{STORAGE_URL}/get_deliveries?start_timestamp={date_time}&end_timestamp={current_timestamp}')
    recent_sales = js.loads(recent_sales_response.content)
    recent_deliveries = js.loads(recent_deliveries_response.content)

    if recent_sales_response.status_code != 200 or recent_deliveries_response.status_code != 200:
        logger.error(f'Received the following status codes - get_daily_sales: {recent_sales.status_code}, get_deliveries: {recent_deliveries.status_code}')
    
    total_events = len(recent_sales) + len(recent_deliveries)
    logger.info(f'Total events since {date_time}: {total_events}')

    print(f'\n\n{json}\n\n{type(recent_sales)}\n{recent_sales}\n\n')

    for sale in recent_sales:
        # REMOVE NEXT LINE WHEN IT WORKS
        print(sale, end='\n***********\n\n')
        json['num_daily_sales_events'] += 1
        if sale['cheeseburgers_sold'] > json['max_cheeseburgers_sold']:
            json['max_cheeseburgers_sold'] = sale['cheeseburgers_sold']
        if sale['fry_servings_sold'] > json['max_fry_servings_sold']:
            json['max_fry_servings_sold'] = sale['fry_servings_sold']
        if sale['hamburgers_sold'] > json['max_hamburgers_sold']:
            json['max_hamburgers_sold'] = sale['hamburgers_sold']
        logger.debug(f'Processed event with trace ID: {sale["trace_id"]}')

    for dlv in recent_deliveries:
        json['num_delivery_events'] += 1
        if dlv['bun_trays_received'] > json['max_bun_trays_received']:
            json['max_bun_trays_received'] = dlv['bun_trays_received']
        if dlv['fry_boxes_received'] > json['max_fry_boxes_received']:
            json['max_fry_boxes_received'] = dlv['fry_boxes_received']
        logger.debug(f'Processed event with trace ID: {dlv["trace_id"]}')
    
    logger.debug(f'Updated statistics --- num_daily_sales_events: {json["num_daily_sales_events"]}' \
        + f', max_cheeseburgers_sold: {json["max_cheeseburgers_sold"]}' \
        + f', max_fry_servings_sold: {json["max_fry_servings_sold"]}' \
        + f', max_hamburgers_sold: {json["max_hamburgers_sold"]}' \
        + f', num_delivery_events: {json["num_delivery_events"]}' \
        + f', max_bun_trays_received: {json["max_bun_trays_received"]}' \
        + f', max_fry_boxes_received: {json["max_fry_boxes_received"]}')

    stats = InventoryStats(json['num_daily_sales_events'],
                           json['max_cheeseburgers_sold'],
                           json['max_fry_servings_sold'],
                           json['max_hamburgers_sold'],
                           json['num_delivery_events'],
                           json['max_bun_trays_received'],
                           json['max_fry_boxes_received'],
                           datetime.datetime.strptime(current_timestamp, "%Y-%m-%dT%H:%M:%SZ"))
    session.add(stats)

    logger.info("Finished Periodic Processing")

    session.commit()
    session.close()

    return json, 200


def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats,
                  'interval',
                  seconds=app_config['scheduler']['period_sec'])
    sched.start()

app = connexion.FlaskApp(__name__, specification_dir='')
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api("processor_api.yaml",
            strict_validation=True,
            validate_responses=True)

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')


if __name__ == "__main__":
    init_scheduler()
    app.run(port=8100, use_reloader=False)