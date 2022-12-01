import swagger_ui_bundle
import connexion
from connexion import NoContent
from datetime import datetime
import yaml
import logging, logging.config
import requests
import json as js
from flask_cors import CORS, cross_origin
import os
from requests.exceptions import ConnectTimeout
from controllers import data_controller

from apscheduler.schedulers.background import BackgroundScheduler


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

RECEIVER_URL = app_config['endpoints']['receiver']
STORAGE_URL = app_config['endpoints']['storage']
PROCESSOR_URL = app_config['endpoints']['processor']
AUDIT_URL = app_config['endpoints']['audit']
REQUEST_TIMEOUT = app_config['endpoints']['timeout_sec']

print(app_config['data']['filepath'])

data_storage = data_controller.Data_Controller(app_config['data']['filepath'])



def poll_services():
    try:
        logger.info(f'Polling {RECEIVER_URL} with timout of {REQUEST_TIMEOUT}')
        res = requests.get(f'{RECEIVER_URL}', timeout=REQUEST_TIMEOUT)
        logger.info(f'Received response from receiver: {res}')
        if res.status_code == 200:
            receiver_response = "Running"
        else:
            receiver_response = "Down"
    except:
        receiver_response = "Down"
    logger.info(f'Receiver service poll returned status {receiver_response}')

    try:
        logger.info(f'Polling {STORAGE_URL} with timout of {REQUEST_TIMEOUT}')
        res = requests.get(f'{STORAGE_URL}', timeout=REQUEST_TIMEOUT)
        if res.status_code == 200:
            storage_response = "Running"
        else:
            storage_response = "Down"
    except:
        storage_response = "Down"
    logger.info(f'Storage service poll returned status {storage_response}')

    try:
        logger.info(f'Polling {PROCESSOR_URL} with timout of {REQUEST_TIMEOUT}')
        res = requests.get(f'{PROCESSOR_URL}', timeout=REQUEST_TIMEOUT)
        if res.status_code == 200:
            processor_response = "Running"
        else:
            processor_response = "Down"
    except:
        processor_response = "Down"
    logger.info(f'Processor service poll returned status {processor_response}')

    try:
        logger.info(f'Polling {AUDIT_URL} with timout of {REQUEST_TIMEOUT}')
        res = requests.get(f'{AUDIT_URL}', timeout=REQUEST_TIMEOUT)
        if res.status_code == 200:
            audit_response = "Running"
        else:
            audit_response = "Down"
    except:
        audit_response = "Down"
    logger.info(f'Audit service poll returned status {audit_response}')

    json = {
        "receiver": receiver_response,
        "storage": storage_response,
        "processor": processor_response,
        "audit": audit_response,
        "last_update": datetime.now()
    }

    data_storage.update_data(json)


def get_health():
    data = data_storage.get_latest_data()
    logger.info(f'Processed request for health stats at {data["last_update"]}')
    return data, 200


def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(poll_services,
                    'interval',
                    seconds=app_config['scheduler']['period_sec'])
    sched.start()


app = connexion.FlaskApp(__name__, specification_dir='')
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api("health-check_api.yaml",
            strict_validation=True,
            validate_responses=True)


if __name__ == "__main__":
    init_scheduler()
    app.run(port=8120)