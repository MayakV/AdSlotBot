import os
import sys
import datetime
# needed to import modules below
parent_dir = os.path.abspath(os.path.join(__file__, os.pardir, os.pardir))
# print(parent_dir)
sys.path.insert(0, parent_dir)

import shared.db as db

db_name = os.getenv("DB_NAME")  # configParser.get('General', 'Db_name')
host = os.getenv("HOSTNAME")   #configParser.get('General', 'Host')
port = int(os.getenv("PORT"))

conn = db.Connection(host, port, db_name)

# conn.update_expired_users()
print("Expired users updated : " + str(conn.update_expired_users()))
conn.update_expired_ads(datetime.timedelta(days=2))
print("Expired ads updated")
