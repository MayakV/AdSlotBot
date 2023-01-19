import os
import sys
import datetime
import logging
# needed to import modules below
parent_dir = os.path.abspath(os.path.join(__file__, os.pardir, os.pardir))
# print(parent_dir)
sys.path.insert(0, parent_dir)

import shared.db as db

db_name = os.getenv("DB_NAME")  # configParser.get('General', 'Db_name')
host = os.getenv("HOSTNAME")   #configParser.get('General', 'Host')
port = int(os.getenv("PORT"))

logFormatter = logging.Formatter("%(asctime)s [chat_bot] [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
rootLogger = logging.getLogger()

# logging to file
fileHandler = logging.FileHandler("/logs/chat_bot.log")
fileHandler.setFormatter(logFormatter)
rootLogger.addHandler(fileHandler)

# logging to console (to stdout and stderr)
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
rootLogger.addHandler(consoleHandler)

conn = db.Connection(host, port, db_name)

# conn.update_expired_users()
logging.info(f"expire_script - истекшие пользователи обновлены: {str(conn.update_expired_users())}")
# conn.update_expired_ads(datetime.timedelta(days=2))
logging.info(f"expire_script - истекших заявок обновлено: {conn.update_expired_ads(datetime.timedelta(days=2))}")
