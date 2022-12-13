import datetime
import time

import telethon.tl.types
from telethon.sync import TelegramClient, events, Message
from telethon import types
from os import getenv
from hashlib import md5
import pprint
from flashtext import KeywordProcessor
import re

from telethon.tl import functions

import filters
import AdSlot
from db import Connection

api_id = int(getenv("AdScraper_api_id"))
api_hash = getenv("AdScraper_api_hash")

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

# with TelegramClient('name', api_id, api_hash) as client:
#    # client.send_message('me', 'Hello, myself!')
#    # print(client.download_profile_photo('me'))
#
#    @client.on(events.NewMessage(pattern='(?i).*Hello'))
#    async def handler(event):
#       await event.reply('Hey!')
#
#
#    client.run_until_disconnected()


with TelegramClient('name', api_id, api_hash) as client:
    async def get_last_message(chat_id):
        async for message in client.iter_messages(chat_id,
                                                  limit=1,
                                                  # offset_date=date_cutoff,
                                                  reverse=False):
            return message.id


    async def get_chat_message(chat_id):
        return [x for x in client.iter_messages(chat_id, limit=10, reverse=True)]


    def get_chat_type(chat):
        if isinstance(chat, types.Channel):
            return 'channel', chat.username
        elif isinstance(chat, types.Chat):
            return 'chat', chat.title
        elif isinstance(chat, types.User):
            return 'user', chat.username
        else:
            return '', ''


    def get_full_name(user: telethon.types.User):
        name = ''
        if user.first_name is not None:
            name += str(user.first_name)
        if user.last_name is not None:
            name += ' ' + str(user.last_name)
        return name


    def get_username(user: telethon.types.User):
        return user.username


    async def main():
        _filter = filters.BuyOrder()
        conn = Connection()
        date_cutoff = datetime.datetime.now() - datetime.timedelta(days=2)
        for chat_id in target_chats_ids:
            chat_info = conn.get_chat_info(chat_id)
            last_analyzed_id = chat_info.get('last_analyzed_id', 0)
            print('getting ' + str(chat_id) + ' history')
            if last_analyzed_id == 0:
                async for message in client.iter_messages(chat_id,
                                                          limit=1,
                                                          # offset_date=date_cutoff,
                                                          reverse=False):
                    last_analyzed_id = max(message.id - 5000, 0)
            async for message in client.iter_messages(chat_id,
                                                      min_id=last_analyzed_id,
                                                      # offset_date=date_cutoff,
                                                      reverse=True):
                # print('analyzing ' + str(message.id) + ' from ' + str(message.date))
                last_analyzed_id = message.id
                if message.date.replace(tzinfo=None) > date_cutoff \
                        and _filter.apply(message.text):
                    # TODO add secondary keyword analysis to determine category, price etc.
                    chat = await client.get_entity(message.peer_id)
                    if isinstance(chat, types.Channel):
                        c_type = 'channel'
                        c_name = chat.username
                    elif isinstance(chat, types.Chat):
                        c_type = 'chat'
                        c_name = chat.title
                    elif isinstance(chat, types.User):
                        c_type = 'user'
                        c_name = chat.username
                    else:
                        c_type = ''
                        c_name = ''
                    users = await client.get_participants(message.from_id)
                    reach_filt = filters.Reach()
                    reach = reach_filt.apply(message.text)
                    bot_comm_message = await message.forward_to(-1001676301152)
                    ad = AdSlot.AdSlot(
                        c_type,
                        chat_id,
                        c_name,
                        message.id,
                        bot_comm_message.id,
                        message.date,
                        message.text,
                    )
                    print(message.id, message.from_id, message.peer_id, message.date, message.post_author, message.text)
                    print(reach)
                    ad.save_to_db(conn)
            conn.update_last_analyzed_id(chat_id, last_analyzed_id)
            # time.sleep(1)


    async def test():
        # async for message in client.iter_messages(5615779963, limit=4000, reverse=False):
        #     print(message.id, message.text)
        async for dialog in client.iter_dialogs():
            print(dialog.name, 'has ID', dialog.id)  # -1001359631606


    async def test_filter():
        # async for message in client.iter_messages(5615779963, limit=4000, reverse=False):
        #     print(message.id, message.text)
        # Adhot = -1001359631606
        # message_id = 773242   тест охвата
        conn = Connection()
        chat_id = 'tgsale'  # 'vpdoc'
        target_message_id = 427005  # 1475156
        chat_info = conn.get_chat_info(chat_id)
        async for message in client.iter_messages(chat_id,
                                                  limit=1,
                                                  min_id=target_message_id-1,
                                                  reverse=True):
            chat = await client.get_entity(message.peer_id)
            c_type, c_name = get_chat_type(chat)
            users = await client.get_participants(message.from_id)

            # reach_filt = filters.Reach()
            # reach = reach_filt.apply(message.text)
            # reach = filters.Reach.apply(message.text)

            _hash = md5(message.text.encode('utf-8')).hexdigest()
            print('Found new message : ' + str(message.id), message.from_id, c_name, message.date,
                  message.post_author,
                  message.text)
            bot_comm_message = await message.forward_to(-1001676301152)
            ad = AdSlot.AdSlot(get_full_name(users[0]),
                               get_username(users[0]),  # message.post_author?
                               # _hash,
                               c_type,
                               chat_id,
                               c_name,
                               message.id,
                               bot_comm_message.id,
                               message.date,
                               message.text,
                               )
            text = filters.prepare_text(message.text)
            ad.apply_secondary_filters(text)
            print(message.id, message.from_id, message.peer_id, message.date, message.post_author)#, message.text)
            # text = ad.get_secondary_filters_message()
            await client.send_message(entity=-1001676301152,
                                      message=ad.get_secondary_filters_message(),
                                      reply_to=bot_comm_message)
            # ad.save_to_db(conn)
        # conn.update_last_analyzed_id(chat_id, last_analyzed_id)


    async def test_last_messae():
        # async for message in client.iter_messages(5615779963, limit=4000, reverse=False):
        #     print(message.id, message.text)
        # Adhot = -1001359631606
        # message_id = 773242   тест охвата
        conn = Connection()
        chat_id = -1484259439
        chat_info = conn.get_chat_info(chat_id)

        async for message in client.iter_messages(chat_id,
                                                  limit=1,
                                                  # min_id=chat_info.get('last_analyzed_id', 0),
                                                  reverse=False):
            chat = await client.get_entity(message.peer_id)
            c_type, c_name = get_chat_type(chat)
            users = await client.get_participants(message.from_id)

            # reach_filt = filters.Reach()
            # reach = reach_filt.apply(message.text)
            reach = filters.Reach.apply(message.text)

            _hash = md5(message.text.encode('utf-8')).hexdigest()
            print('Found new message : ' + str(message.id), message.from_id, c_name, message.date,
                  message.post_author,
                  message.text)
            bot_comm_message = await message.forward_to(-1001676301152)
            ad = AdSlot.AdSlot(get_full_name(users[0]),
                               get_username(users[0]),  # message.post_author?
                               _hash,
                               c_type,
                               chat_id,
                               c_name,
                               message.id,
                               bot_comm_message.id,
                               message.date,
                               message.text,
                               )
            await client.send_message(entity=-1001676301152, message="Ответы работают", reply_to=bot_comm_message)
            #ad.save_to_db(conn)
        #conn.update_last_analyzed_id(chat_id, last_analyzed_id)


    async def test_date():
        date_cutoff = datetime.datetime.now() - datetime.timedelta(days=2)
        async for message in client.iter_messages('AdHotChat',
                                                  min_id=780777,
                                                  # offset_date=date_cutoff,
                                                  reverse=True):
            # print('analyzing ' + str(message.id) + ' from ' + str(message.date))
            last_analyzed_id = message.id
            _filter = filters.BuyOrder()
            if message.date.replace(tzinfo=None) > date_cutoff \
                    and _filter.apply(message.text):
                # TODO add secondary keyword analysis to determine category, price etc.
                chat = await client.get_entity(message.peer_id)
                if isinstance(chat, types.Channel):
                    c_type = 'channel'
                    c_name = chat.username
                elif isinstance(chat, types.Chat):
                    c_type = 'chat'
                    c_name = chat.title
                elif isinstance(chat, types.User):
                    c_type = 'user'
                    c_name = chat.username
                else:
                    c_type = ''
                    c_name = ''
                users = await client.get_participants(message.from_id)
                reach_filt = filters.Reach()
                reach = reach_filt.apply(message.text)
                # bot_comm_message = await message.forward_to(-1001676301152)
                ad = AdSlot.AdSlot(users[0],
                                   c_type,
                                   chat.id,
                                   c_name,
                                   message.id,
                                   0,  # bot_comm_message.id,
                                   message.date)
                print(message.id, message.from_id, message.peer_id, message.date, message.post_author, message.text)
                print(reach)
                print(message.date.replace(tzinfo=None) > date_cutoff)

    async def print_chats():
        request = await client(functions.messages.GetDialogFiltersRequest())
        f = list(filter(lambda x: x.get("title", "") == 'Реклама', [diag.to_dict() for diag in request]))
        if f and len(f) == 1:
            ad_folder = f[0]
        else:
            raise ValueError("Folder with name \'Реклама\' not found")

        for dialog in ad_folder["include_peers"]:
            _id = dialog.get("channel_id", dialog.get("chat_id", dialog.get("user_id", "")))
            if _id:
                ent = await client.get_entity(_id)
                pprint.pprint(ent)
        # for dialog in client.iter_dialogs():
        #     pprint.pprint(dialog.name + " - " + str(dialog.entity.username) + " - " + str(dialog.id))
        #     time.sleep(2)

    async def test_get_chat():
        _id = 1319627761
        ent = await client.get_entity(telethon.tl.types.PeerChat(_id))
        try:
            ent = await client.get_entity(_id)
        except ValueError:
            ent = await client.get_entity(telethon.tl.types.PeerChat(_id))
        except telethon.errors.ChatIdInvalidError:
            ent = await client.get_entity(telethon.tl.types.PeerChannel(_id))
        print(ent)

    async def test_buy_order():
        keyword_list = ['AдXот']
        processor = KeywordProcessor()
        processor.add_keywords_from_list(keyword_list)
        txt = '''[Fo'''
        kw = processor.extract_keywords(txt)
        print(kw)


    def prepare_text(text):
        text = text.replace(r'`', '')
        text = re.sub(r'(\d+) (\d+)', r'\1\2', text)
        # text = re.sub(r'(\d+)([кk]?)\s?-\s?(\d+)([кk]?)', r'\1\2-\3\4', text)
        text = re.sub(r'(от )?(\d+)\s?[кk]?\s?(-|до)\s?(\d+)\s?[кk]', r'\g<1>000-\g<2>000', text)
        text = re.sub(r'(\d+)\s?[kк]', r'\g<1>000', text)
        text = re.sub(r'[*?._\'\"# ]+', r' ', text)
        number_symbols = {'1️⃣': '1',
                          '2️⃣': '2',
                          '3️⃣': '3',
                          '4️⃣': '4',
                          '5️⃣': '5',
                          '6️⃣': '6',
                          '7️⃣': '7',
                          '8️⃣': '8',
                          '9️⃣': '9',
                          '0️⃣': '0',
                          '➕': '+'}
        # pattern = re.compile(r'\b(' + '|'.join(number_symbols.keys()) + r')\b')
        pattern = re.compile(u'1️⃣|2️⃣|3️⃣|4️⃣|5️⃣|6️⃣|7️⃣|8️⃣|9️⃣|0️⃣|➕')
        text = pattern.sub(lambda x: number_symbols[x.group()], text)
        # text = re.sub(u'1️⃣ | 2 | 2️⃣ | 4 | 5️⃣ | 6 | 7 | 8 | 9️⃣ |0️⃣', convert_number_symbols, text) #
        # print(text)
        return text

    async def test_buy_channel():
        text = '''КУПЛЮ ВЕЧЕРА на СЛЕДУЮЩИЕ ДНИ 2-8к охв под фулл
(НЕ ПОД ПРИВАТ)

ПИШИТЕ ВСЕ, ПЛЗ!
👈 👈 👈 СТАТА, ЛИНК, ЦЕНА, ДАТА'''
        txt = prepare_text(text)
        keyw, exc_keyw = filters.BuyOrder.apply(text)
        print(txt)
        print(keyw)
        print(exc_keyw)


    client.loop.run_until_complete(test_buy_channel())
    # pay.poll_yoomoney_operations()
    conn = Connection()
    # conn.update_expired_users()
    # conn.update_expired_ads(datetime.timedelta(days=2))
    # import scraper
    # scraper.scraper_poll()
    # print(datetime.timedelta(days=2, months=0))

