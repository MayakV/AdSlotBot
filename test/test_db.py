import datetime

from pymongo import MongoClient, collection, cursor
from bson import ObjectId
import pprint
import hashlib
import os
import sys

from pymongo.database import Database

parent_dir = os.path.abspath(os.path.join(__file__, os.pardir, os.pardir))
print(parent_dir)
sys.path.insert(0, parent_dir)

import db

#  TODO добавить обработчик для удаленных каналов
t = [-1089694021,  #
     'AdHotChat',
     'birzha_chat69',
     'tgsale',
     'Advertising_exchange_1',
     'Advertjsjng_Telegram',
     'alice_bob_public',
     'birgarekl', # TODO
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
     'easy_reklama',  #
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
     'Reklama_chat',  #
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
     'tgbirza',  #
     'TGBIRZGA',
     'tgsale',
     'tg_chat3',
     'tg_sale',
     'tolko_pokypka',
     'TOPadvPlace',
     'toppadminchat',
     'vpdoc',
     'youradvt',
     'birja_Chat_Dok', # TODO
     'pokupkanovosti',
     'PokupkaTrash',
     'AdHotBirzhaChat', # каналы?
     'AdHotChat',
     'crypto_adminu',
     'tg_chat3',
     'reklamateladm',
     'adm_telegram',
     'tgm_adm',
     'tgm_trade',
     'trade_tgm',
     'Reklama_grami',
     'dvijenie_telegram',
     -897864092,
-1001152945968,
-1001404654685,
-1001448211813,
-1001301229291,
-1001357225252,
-1001344021287,
-1001484259439
     ]

# print(target_chats_ids)


# slot = AdSlot('Dshar')

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


def add_chats(conn, chats):
    # TODO save chat names by getting them from telegram API
    conn.add_chats(chats)


def populate_bill_periods(conn: db.Connection):
    conn.add_bill_period(396170593, 'TRIAL', '3d')
    conn.add_bill_period(1004977105, 'TRIAL', '3d')
    conn.add_bill_period(396170593, '719080979673002012', '7d')


def rescan_chats(client: Database):
    collect = client['chats']
    collect.update_many({'last_analyzed_id': {'$gt': 0}}, {'$set': {'last_analyzed_id': 0}})
    collect = client['ads']
    collect.delete_many({})


client = MongoClient()
db1 = client['AdSlot_db_prod']
collect = db1['chats']
# slot.save_to_db(collect)    AdSlot_TOKEN

# cur = collect.find()
# cur = collect.find({'author_username': 'lisste'})
# c = db['test-collection']
# collect.drop()

# cur = collect.find({"_id": ObjectId('630d0e308a90b74fe7223aca')})

# Нужно вытаскивать сообщения со ссылками на каналы (не ботов)
conn = db.Connection()
# reinsert_user(conn)
# clear_user_filters(conn)

# cur = collect.find({'user_id': 396170593})

# collect.delete_many({})
# add_chats(conn, t)

rescan_chats(db1)
# cur = collect.find({'bot_comm_message_id': 1792})
# 7rypEOoE9kY3OTIy
cur = collect.find()
pprint.pp(list(cur))

# print(hashlib.md5('КУПЛЮ ВЕЧЕР сегодня 2-8к охв под фулл или выше'.encode('utf-8')).hexdigest())
#
# lis = [669256.02, 6117662.09, 669258.61, 6117664.39, 669258.05, 6117665.08]
# it = iter(lis)
# for x in it:
#     print (x, next(it))

def reindent(s, numSpaces):
    s = s.split('\n')
    s = [(numSpaces * ' ') + line.lstrip() for line in s]
    # s = s.join('\r\n')
    s = '\n'.join(s)
    return s

txt = '''Здравствуйте, продам рекламу на канале, который входит в **ТОП-5 в тематике Психология** и **в ТОП-5 в тематике Цитаты **🔥

**95% Женщины РФ 20-35 лет, Максимально платежеспособная аудитория

**Сегодня и завтра закупаем рекламу в других каналах на 20.000₽

#психология #саморазвитие #жца #продамрекламу #продажа

💎Закупаем рекламу каждый день
📱Трафик TG + Instagram
👥Подписчики: 200.000
📈Статистика +++

1/24-3990₽
2/24 - 4490₽
2/48 - 5090₽
3/72 - 5490₽
3/ без удаления - 5999₽

💎**3/без удаления + 7 дней в закреплённом сообщении - 9999**₽💎

**📝РЕКЛАМНЫЕ ОТЗЫВЫ: **@MYSLI_OTZIV

**✅КАНАЛ:** @Psikhologia_Tsitaty

❗️ПИСАТЬ АДМИНУ: @MYSLI_ADMIN'''

print(txt)
print(reindent(txt, 4))