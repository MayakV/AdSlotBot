import datetime
import time
from hashlib import md5

import telethon.tl.types
from telethon.sync import TelegramClient, events, Message
from telethon import types
from os import getenv

from telethon.tl import functions

import filters
from AdSlot import AdSlot
from db import Connection

api_id = int(getenv("AdScraper_api_id"))
api_hash = getenv("AdScraper_api_hash")



with TelegramClient('name', api_id, api_hash) as client:
    async def get_last_message(chat_id):
        async for message in client.iter_messages(chat_id,
                                                  limit=1,
                                                  # offset_date=date_cutoff,
                                                  reverse=False):
            return message.id

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
        # _filter = filters.BuyOrder()
        conn = Connection()
        date_cutoff = datetime.datetime.now() - datetime.timedelta(days=2)
        chat_ids = [x['chat_id'] for x in conn.get_chats()]

        for chat_id in chat_ids:
            chat_info = conn.get_chat_info(chat_id)
            last_analyzed_id = chat_info.get('last_analyzed_id', 0)
            print('getting ' + str(chat_id) + ' history')
            # only 5000 messages get analyzed
            if last_analyzed_id < (id_cutoff := await get_last_message(chat_id) - 5000):  # or last_analyzed_id == 0
                last_analyzed_id = id_cutoff

            async for message in client.iter_messages(chat_id,
                                                      min_id=last_analyzed_id,
                                                      reverse=True):
                last_analyzed_id = message.id
                if message.date.replace(tzinfo=None) > date_cutoff and filters.BuyOrder.apply(message.text):
                    chat = await client.get_entity(message.peer_id)
                    c_type, c_name = get_chat_type(chat)
                    users = await client.get_participants(message.from_id)

                    # reach_filt = filters.Reach()
                    # reach = reach_filt.apply(message.text)
                    # reach = filters.Reach.apply(message.text)

                    _hash = md5(message.text.encode('utf-8')).hexdigest()
                    ad_info = conn.get_ad_info(get_username(users[0]), _hash)
                    if ad_info:
                        ad = AdSlot(ad_info.get('author_name', ''),
                                    ad_info.get('author_username', ''),
                                    # ad_info.get('message_hash', ''),
                                    ad_info.get('original_chat_type', ''),
                                    ad_info.get('original_chat_id', 0),
                                    ad_info.get('original_chat_name', ''),
                                    ad_info.get('message_id', 0),
                                    ad_info.get('bot_comm_message_id', 0),
                                    ad_info.get('date_published', datetime.datetime(1970, 1, 1)),
                                    ad_info.get('text', ''),
                                    status=ad_info.get('status', ''),
                                    secondary_filter_params=ad_info.get('secondary_filter_params', {}),
                                    )
                        print('Found duplicate message : ' + str(message.id), ad.message_hash,
                              ad.author_username, ad.original_chat_name)
                        ad.set_date(message.date)
                        ad.set_original_chat(c_type, chat_id, c_name)
                        ad.set_author(get_full_name(users[0]), get_username(users[0]))
                        ad.set_message_id(message.id)
                        ad.set_status('open')
                    else:
                        print('Found new message : ' + str(message.id), message.from_id, c_name, message.date,
                              message.post_author,
                              message.text)
                        bot_comm_message = await message.forward_to(-1001676301152)
                        ad = AdSlot(get_full_name(users[0]),
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
                        await client.send_message(entity=-1001676301152,
                                                  message=ad.get_secondary_filters_message(),
                                                  reply_to=bot_comm_message)
                    ad.save_to_db(conn)
            conn.update_last_analyzed_id(chat_id, last_analyzed_id)

    client.loop.run_until_complete(main())
