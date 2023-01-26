import os
from pathlib import Path
import sys
import datetime
import logging

# needed to import modules below
parent_dir = os.path.abspath(os.path.join(__file__, os.pardir, os.pardir))
sys.path.insert(0, parent_dir)

import shared.db as db

db_name = os.getenv("DB_NAME")  # configParser.get('General', 'Db_name')
host = os.getenv("HOSTNAME")   #configParser.get('General', 'Host')
port = int(os.getenv("PORT"))

log_folder_path = Path(os.getenv("ADSLOT_LOGS_FOLDER"))

logging.basicConfig(
        filename=log_folder_path / 'chat_bot.log',
        format='%(asctime)s [expire_script] [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=logging.INFO)

conn = db.Connection(host, port, db_name)

# conn.update_expired_users()
logging.info(f"Истекшие пользователи обновлены: {str(conn.update_expired_users())}")
# conn.update_expired_ads(datetime.timedelta(days=2))
logging.info(f"Истекших заявок обновлено: {conn.update_expired_ads(datetime.timedelta(days=2))}")
