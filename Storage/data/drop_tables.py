import sqlite3

conn = sqlite3.connect('lab3_storage.sqlite')

c = conn.cursor()
c.execute('''
          DROP TABLE daily_sales
          ''')

c.execute('''
          DROP TABLE delivery
          ''')

conn.commit()
conn.close()
