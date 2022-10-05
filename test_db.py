import datetime

from pymongo import MongoClient, collection, cursor
from bson import ObjectId
from AdSlot import AdSlot
import pprint
import hashlib
import db

target_chats_ids = [  # -1089694021,
    'AdHotChat',
    'birzha_chat69',
    'tgsale',
    'Advertising_exchange_1',
    'Advertjsjng_Telegram',
    'alice_bob_public',
    'birgarekl',
    'birga_ru',
    'birjaga',
    'birza_kanalov',
    'birzha_chat69',
    'birzha_kanaIov',
    'birzha_reklamy2',
    'booklt',
    'boom_chat2',
    'brt_tg2',
    'chattte',
    # 'easy_reklama',
    'exchangeres',
    'exchange_reklama',
    'FamilyPR',
    'fieryTGadmin',
    'goodpiarTG',
    'GUMarket_ads',
    'Helix_shop_Chat0',
    'marketingchat_ru',
    'marketprooo',
    'only_pokupka',
    'piarNOpar',
    'reclamarket',
    'reclama_room',
    'reclapoh',
    'rekbir',
    'reklamakp',
    'reklamarur',
    'reklamateladm',
    'Reklamazdess',
    'Reklama_ADD',
    # 'Reklama_chat',
    'reklama_chat_bazar',
    'Reklama_grami',
    'reklamka03',
    'reklamka_2020',
    'reklam_birzha',
    'reklmam',
    'rinochek105',
    'RuProB',
    'swap_room',
    'Tadverts',
    'telegabirga',
    'telegads',
    'telega_Admins',
    # 'tgbirza',
    'TGBIRZGA',
    'tgsale',
    'tg_chat3',
    'tg_sale',
    'tolko_pokypka',
    'TOPadvPlace',
    'toppadminchat',
    'vpdoc',
    'youradvt',
]


#slot = AdSlot('Dshar')

# d = {'author': 'Pupkin', 'price': 20, 'price_units': 'km/h'}

# new_user = {'user_id': 396170594,
#             'join_date': datetime.datetime.now() - datetime.timedelta(days=60),
#             'payment_status': 'confirmed'}
# new_bill_period = {'user_id': 396170594,
#                    'bill_id': 717601863256002029,
#                    'valid_from': datetime.datetime.now() - datetime.timedelta(days=32),
#                    'valid_to': datetime.datetime.now() - datetime.timedelta(days=1)}
# collect = db['users']
# collect.update_one({'user_id': 396170594}, {'$set': new_user}, upsert=True)
# collect = db['bill_periods']
# collect.update_one({'bill_id': 717601863256002029}, {'$set': new_bill_period}, upsert=True)

# collect = db['users']
# collect.update_one({'user_id': '396170593'}, {"$set": {"user_id": 396170593}})

# collect.delete_one({'user_id': '396170594'})

# d = {'chat_id': 'AdHotChat', 'last_analyzed_id': 783338}
# collect.insert_one(d)


def reinsert_user(conn):
    # d = {'user_id': 536303432, 'join_date': datetime.datetime(2022, 9, 27, 16, 39, 13, 791000), 'payment_status': 'confirmed'}
    conn.delete_user(536303432)
    conn.clear_user_bill_history(536303432)
    # conn.create_user(536303432, datetime.datetime(2022, 9, 27, 16, 39, 13, 791000), 'confirmed')

client = MongoClient()
db1 = client['test-database']
collect = db1['users']
#slot.save_to_db(collect)    AdSlot_TOKEN

# cur = collect.find()
# cur = collect.find({'author_username': 'lisste'})
# c = db['test-collection']
# collect.drop()
# collect = db['chats']
# collect.update_many({'last_analyzed_id': {'$gt': 0}}, {'$set': {'last_analyzed_id': 0}})
#cur = collect.find({"_id": ObjectId('630d0e308a90b74fe7223aca')})

# Нужно вытаскивать сообщения со ссылками на каналы (не ботов)
conn = db.Connection()
reinsert_user(conn)

cur = collect.find()
pprint.pp(list(cur))

# print(hashlib.md5('КУПЛЮ ВЕЧЕР сегодня 2-8к охв под фулл или выше'.encode('utf-8')).hexdigest())
