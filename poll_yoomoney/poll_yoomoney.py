import datetime
import logging
import os
from pathlib import Path
import sys

# needed to import modules below
parent_dir = os.path.abspath(os.path.join(__file__, os.pardir, os.pardir))
sys.path.insert(0, parent_dir)

import shared.bill as bill
import shared.db as db

log_folder_path = Path(os.getenv("ADSLOT_LOGS_FOLDER"))

logging.basicConfig(
        filename=log_folder_path / 'chat_bot.log',
        format='%(asctime)s [poll_yoomoney] [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=logging.INFO)

db_name = os.getenv("DB_NAME")  # configParser.get('General', 'Db_name')
host = os.getenv("HOSTNAME")   #configParser.get('General', 'Host')
port = int(os.getenv("PORT"))

conn = db.Connection(host, port, db_name)

logging.info("Запрос обновлений с yoomoney")
dt = conn.get_last_bill_date()
if dt:
    operations = bill.get_new_operations(dt)
else:
    operations = bill.get_new_operations(datetime.datetime.strptime('1970/01/01 00:00:00', '%Y/%m/%d %H:%M:%S'))
if operations:
    for operation in operations:
        if operation.direction == 'in' and operation.status == 'success':
            # t = conn.get_new_bill(operation.operation_id)
            if not conn.get_bill(operation.operation_id):  # conn.get_new_bill(operation.operation_id)
                user_id, *period = operation.label.split('_')
                if period and len(period) == 1:
                    logging.info(f"Найдена новая операция {operation.operation_id} с меткой {operation.label}")
                    conn.save_bill(operation.operation_id,
                                   int(user_id),
                                   operation.datetime,
                                   period[0],
                                   operation.amount)
                    conn.add_bill_period(int(user_id), operation.operation_id, period[0])
                    conn.permit_user(int(user_id))
                else:
                    pass  # raise no period specified?
else:
    logging.info(f"Не найдено новых операций")
