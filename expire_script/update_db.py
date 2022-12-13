import os
import sys
import datetime

parent_dir = os.path.abspath(os.path.join(__file__, os.pardir, os.pardir))
sys.path.insert(0, parent_dir)

import db

conn = db.Connection()

# conn.update_expired_users()
print("Expired users updated : " + str(conn.update_expired_users()))
conn.update_expired_ads(datetime.timedelta(days=2))
print("Expired ads updated")
