import sqlite3

conn = sqlite3.connect('lab3_storage.sqlite')

c = conn.cursor()

c.execute('''
            CREATE TABLE daily_sales
            (id INTEGER PRIMARY KEY ASC,
            restaurant_id VARCHAR(250) NOT NULL,
            inventory_datetime VARCHAR(100) NOT NULL,
            cheeseburgers_sold INTEGER,
            hamburgers_sold INTEGER,
            fry_servings_sold INTEGER,
            trace_id INTEGER)
            ''')

c.execute('''
            CREATE TABLE delivery
            (id INTEGER PRIMARY KEY ASC,
            restaurant_id VARCHAR(250) NOT NULL,
            delivery_id INTEGER NOT NULL,
            delivery_datetime VARCHAR(100) NOT NULL,
            bun_trays_received INTEGER,
            cheese_boxes_received INTEGER,
            fry_boxes_received INTEGER,
            patty_boxes_received INTEGER,
            trace_id INTEGER)
          ''')

conn.commit()
conn.close()