import sqlite3
import yaml

with open('../app_conf.yml', 'r') as f:
    conf = yaml.safe_load(f.read())

db_name = conf['datastore']['filename']

conn = sqlite3.connect(db_name)

c = conn.cursor()


c.execute('''
            CREATE TABLE InventoryStats
            (id INTEGER PRIMARY KEY ASC,
            num_daily_sales_events INTEGER NOT NULL,
            max_cheeseburgers_sold INTEGER,
            max_fry_servings_sold INTEGER,
            max_hamburgers_sold INTEGER,
            num_delivery_events INTEGER NOT NULL,
            max_bun_trays_received INTEGER,
            max_fry_boxes_received INTEGER,
            last_updated VARCHAR(100) NOT NULL)
          ''')






        # - num_daily_sales_events
        # - max_cheeseburgers_sold
        # - max_fry_servings_sold
        # - max_hamburgers_sold
        # - num_delivery_events
        # - max_bun_trays_received
        # - max_fry_boxes_received


conn.commit()
conn.close()