import sqlite3

def create_tables(db_name):
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

  conn.commit()
  conn.close()