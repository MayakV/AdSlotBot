import datetime

from pymongo import MongoClient, collection, cursor
from bson import ObjectId
import pprint
import hashlib
import db

#  TODO добавить обработчик для удаленных каналов
t = [  -1089694021, #
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
    'easy_reklama', #
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
    'Reklama_chat', #
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
    'tgbirza', #
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

t1 = [ 'birja_Chat_Dok',
'+AY8kjWpE_U4wODc6',
'pokupkanovosti',
'PokupkaTrash',
'AdHotBirzhaChat',
'AdHotChat',
'7rypEOoE9kY3OTIy',
'crypto_adminu',
'tg_chat3',
'reklamateladm',
'+7sDWuorXQ0hiMDVi',
'+0pecYNr9sH1hYzZi',
'+1KLxyVaVX1E5OTgy',
'+sDWLbNAaxEg3MWQy',
'+EbU_8ZkkQBIxMjRi',
'+2UFhMaxrQVk0NjUy',
'+CiWvkww3qCZlNGVi',
'+DRBAnSMQu2JkYzIy',
'+77FJR676i3c5ZWYy',
'+233WUAoflDcwNjBi',
'+Fu3_oGbfTVBiZDRi',
'+HI8lBOMl2do4YmNi',
'+HY602kycZK9kMDVi',
'+GAha9KymF584MzIy',
'+ajN1eVpqUMk0NWJi',
'+T5ZIEqlu19M2MGEy',
'+mrP6ZkIOID1hMGNi',
'+Y9IVESLYHrlkMWQy',
'+u7PVQHCsEqk0MzY6',
'+oB_b5q2zF1YxMjFi',
'+qPKvjpJA9GE3MzY6',
'+5GwtnIpJxdBmZmUy',
'+I5C4350uvm82ZWEy',
'+OglxuCHdyno1YzU6',
'+ZWyis-IMAQljYmYy',
'+IXvm0KhDzV83NTM6',
'+hJbkhbBO_540Y2Fi',
'+ZvyO25hfO4o1NGIy',
'+6IDDBiy2W7dhNWU6',
'+ux4eWiikn8wyOTJi',
'+DbTbk46LCVhiMjRi',
'+-Og9StVBcU8wNjRi',
'adm_telegram',
'tgm_adm',
'tgm_trade',
'trade_tgm',
'+qSHHb07VCm8zNTEy',
'+liIqW62D0kVlNzZi',
'+08prMWpnozg5NjZh',
'+dyen3bU65VBhYmJi',
'+z12CYsIbtrkxYzZh',
'+fQ0ZAAsetodkMGZi',
'+Po7Kjl6GTrlhMzRi',
'+8b0xNR4WaH9mZTFi',
'+Ld4BggAk8KszNTZh',
'+iGaRzs9IDKo0Y2Qy',
'+NVUl3pmRGOIwMmMx',
'+o0UkYEKA44A1YzJh',
'+2OV6mVrJRWkyZDky',
'+cDHaVzQdYrYwNDRi',
'+24dusMZlQgk4OTcy',
'+0jIVcFn-8gtmOWI6',
'+M2TwyjbS2NliNmMy',
'+1K4pIe73QZQ4MTUy',
'+YczkQTbfxys0OTBi',]

target_chats_ids = set(t)
target_chats_ids.update(set(t1))
target_chats_ids = list(target_chats_ids)

# print(target_chats_ids)


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

def clear_user_filters(conn):
    # d = {'user_id': 536303432, 'join_date': datetime.datetime(2022, 9, 27, 16, 39, 13, 791000), 'payment_status': 'confirmed'}
    conn.clear_user_filters(536303432)
    # conn.create_user(536303432, datetime.datetime(2022, 9, 27, 16, 39, 13, 791000), 'confirmed')

def add_chats(conn):
    conn.add_chats(target_chats_ids)

def populate_bill_periods(conn : db.Connection):
    conn.add_bill_period(396170593, 'TRIAL', '3d')
    conn.add_bill_period(1004977105, 'TRIAL', '3d')
    conn.add_bill_period(396170593, '719080979673002012', '7d')

client = MongoClient()
db1 = client['AdSlot_db_prod']
collect = db1['bill_periods']
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
# reinsert_user(conn)
# clear_user_filters(conn)

# cur = collect.find({'user_id': 396170593})
# add_chats(conn)
cur = collect.find()
pprint.pp(list(cur))

# print(hashlib.md5('КУПЛЮ ВЕЧЕР сегодня 2-8к охв под фулл или выше'.encode('utf-8')).hexdigest())
#
# lis = [669256.02, 6117662.09, 669258.61, 6117664.39, 669258.05, 6117665.08]
# it = iter(lis)
# for x in it:
#     print (x, next(it))