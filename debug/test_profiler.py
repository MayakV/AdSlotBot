# import yappi
# import user_filters
# import db
import bill

from pymongo import MongoClient, collection, cursor
from bson import ObjectId
import pprint
import hashlib

client = MongoClient()
db1 = client['AdSlot_db_prod']
collect = db1['ads']

cur = collect.find()
pprint.pp(list(cur))

operations = bill.get_new_operations(datetime.datetime.strptime('1970/01/01 00:00:00', '%Y/%m/%d %H:%M:%S'))

# with yappi.run(builtins=True):
#     conn = db.Connection()
#     _filter = user_filters.Category
#     ads = conn.get_ads()
#     ads = _filter.apply(conn, 536303432, ads)
#     print(len(ads))

#
# print("================ Func Stats ===================")
#
# yappi.get_func_stats().print_all()
#
# print("\n================ Thread Stats ===================")
#
# yappi.get_thread_stats().print_all()
#
#
# print("\nYappi Backend Types   : ",yappi.BACKEND_TYPES)
# print("Yappi Clock Types     : ", yappi.CLOCK_TYPES)
# print("Yappi Stats Columns   : ", yappi.COLUMNS_FUNCSTATS)
# print("Yappi Line Sep        : ", yappi.LINESEP)

