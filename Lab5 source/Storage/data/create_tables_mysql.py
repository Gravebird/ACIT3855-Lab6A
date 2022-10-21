import mysql.connector
import yaml

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

db_conn = mysql.connector.connect(
    host=app_config['datastore']['hostname'], 
    user=app_config['datastore']['user'],
    password=app_config['datastore']['password'], 
    database=app_config['datastore']['db'])

db_cursor = db_conn.cursor()

db_cursor.execute('''
                    CREATE TABLE daily_sales
                    (
                        id INT NOT NULL AUTO_INCREMENT,
                        restaurant_id VARCHAR(250) NOT NULL,
                        inventory_datetime VARCHAR(100) NOT NULL,
                        cheeseburgers_sold INT DEFAULT 0,
                        hamburgers_sold INT DEFAULT 0,
                        fry_servings_sold INT DEFAULT 0,
                        trace_id INT NOT NULL,
                        PRIMARY KEY (id)
                    );
                  ''')

db_cursor.execute('''
                    CREATE TABLE delivery
                    (
                        id INT NOT NULL AUTO_INCREMENT,
                        restaurant_id VARCHAR(250) NOT NULL,
                        delivery_id INT NOT NULL,
                        delivery_datetime VARCHAR(100) NOT NULL,
                        bun_trays_received INT DEFAULT 0,
                        cheese_boxes_received INT DEFAULT 0,
                        fry_boxes_received INT DEFAULT 0,
                        patty_boxes_received INT DEFAULT 0,
                        trace_id INT NOT NULL,
                        PRIMARY KEY (id)
                    );
                  ''')

db_conn.commit()
db_conn.close()