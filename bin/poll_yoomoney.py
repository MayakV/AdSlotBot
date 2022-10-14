import datetime
import logging
import os
import sys

parent_dir = os.path.abspath(os.path.join(__file__, os.pardir, os.pardir))
sys.path.insert(0, parent_dir)

import bill
import db

print("Polling yoomoney")

conn = db.Connection()

p = os.path.join(os.path.abspath(os.path.join(__file__, os.pardir, os.pardir)), 'log', r'yoomoney.log')

logging.basicConfig(filename=p, encoding='utf-8', level=logging.INFO, format='%(asctime)s %(message)s')

dt = conn.get_last_bill_date()
if dt:
    operations = bill.get_new_operations(dt)
else:
    operations = bill.get_new_operations(datetime.datetime.strptime('1970/01/01 00:00:00', '%Y/%m/%d %H:%M:%S'))
for operation in operations:
    if operation.direction == 'in' and operation.status == 'success':
        # t = conn.get_new_bill(operation.operation_id)
        if not conn.get_bill(operation.operation_id):  # conn.get_new_bill(operation.operation_id)
            user_id, *period = operation.label.split('_')
            if period and len(period) == 1:
                logging.info("Found new operations %s with label %s", operation.operation_id, operation.label)
                conn.save_bill(operation.operation_id,
                               int(user_id),
                               operation.datetime,
                               period[0],
                               operation.amount)
                conn.add_bill_period(int(user_id), operation.operation_id, period[0])
                conn.permit_user(int(user_id))
            else:
                pass  # raise no period specified?
