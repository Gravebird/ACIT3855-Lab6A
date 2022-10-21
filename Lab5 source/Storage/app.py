import swagger_ui_bundle
import connexion
import yaml
import logging, logging.config
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

def upload_sales(body):
    """ Receives an upload sales event """

    session = DB_SESSION()

    daily_sales = DailySales(body['restaurant_id'], body['cheeseburgers_sold'],
                body['hamburgers_sold'], body['fry_servings_sold'], body['trace_id'])
    
    session.add(daily_sales)

    session.commit()
    session.close()

    logger.debug(f'Stored event "upload_sales" request with a trace id of {body["trace_id"]}')

    return NoContent, 201


def upload_delivery(body):
    """ Receives an upload delivery event """

    session = DB_SESSION()

    delivery = Delivery(body['restaurant_id'], body['delivery_id'],
                body['bun_trays_received'], body['cheese_boxes_received'],
                body['fry_boxes_received'], body['patty_boxes_received'], body['trace_id'])

    session.add(delivery)

    session.commit()
    session.close()

    logger.debug(f'Stored event "upload_delivery" request with a trace id of {body["trace_id"]}')

    return NoContent, 201


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


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("storage_api.yaml",
            strict_validation=True,
            validate_responses=True)

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')


if __name__ == "__main__":
    app.run(port=8090)