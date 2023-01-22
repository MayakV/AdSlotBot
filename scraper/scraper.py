import datetime
from hashlib import md5
import telethon.tl.types
from telethon.sync import TelegramClient
from telethon import types
import os
import configparser
import sys
from telethon.tl import functions
import logging

# needed to import modules below
parent_dir = os.path.abspath(os.path.join(__file__, os.pardir, os.pardir))
sys.path.insert(0, parent_dir)

import shared.filters as filters
from shared.AdSlot import AdSlot
from shared.db import Connection

# configParser = configparser.RawConfigParser()
# configFilePath = os.path.join(os.path.abspath(os.path.join(__file__, os.pardir, os.pardir)), 'config',
#                               r'scraper_config.txt')
# configParser.read(configFilePath)

db_name = os.getenv("DB_NAME")  # configParser.get('General', 'Db_name')
host = os.getenv("HOSTNAME")   #configParser.get('General', 'Host')
port = int(os.getenv("PORT"))

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")

hours_to_scrape = int(os.getenv("HOURS_TO_SCRAPE"))

logging.basicConfig(
        filename='/home/scraper/logs/scraper.log',
        format='%(asctime)s [scraper      ] [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=logging.INFO)

dbg_mode = True

# TODO load table of ad hashes first, compare duplicates there before applying all the filters


def reindent(s, num_spaces):
    if num_spaces:
        s = s.split('\n')
        s = [(num_spaces * ' ') + line.lstrip() for line in s]
        # s = s.join('\r\n')
        s = '\n'.join(s)
    return s


with TelegramClient('name', api_id, api_hash) as client:
    async def get_last_message(chat_id):
        async for message in client.iter_messages(chat_id,
                                                  limit=1,
                                                  # offset_date=date_cutoff,
                                                  reverse=False):
            return message.id


    def get_chat_type(chat):
        if isinstance(chat, types.Channel):
            return 'channel'
        elif isinstance(chat, types.Chat):
            return 'chat'
        elif isinstance(chat, types.User):
            return 'user'
        else:
            return '', ''


    def get_chat_username(chat):
        if isinstance(chat, types.Channel):
            return chat.username
        elif isinstance(chat, types.Chat):
            return None  # chat cannot have a username
        elif isinstance(chat, types.User):
            return chat.username
        else:
            raise TypeError("Cannot get username. Unknown type of chat entity")


    def get_chat_title(chat):
        if isinstance(chat, types.Channel):
            return chat.title
        elif isinstance(chat, types.Chat):
            return chat.title  # chat cannot have a username
        elif isinstance(chat, types.User):
            return chat.username
        else:
            raise TypeError("Cannot get username. Unknown type of chat entity")


    def get_full_name(user: telethon.types.User):
        name = ''
        if user.first_name is not None:
            name += str(user.first_name)
        if user.last_name is not None:
            name += ' ' + str(user.last_name)
        return name


    def get_username(user: telethon.types.User):
        return user.username


    async def update_chats(conn: Connection):
        request = await client(functions.messages.GetDialogFiltersRequest())
        f = list(filter(lambda x: x.get("title", "").startswith('Реклама'), [diag.to_dict() for diag in request]))
        # two folders with the same name cannot exist, so it's either 0 or 1
        if not len(f):
            raise ValueError("Folders starting with \'Реклама\' not found")

        peers = []
        for folder in f:
            peers = peers | folder["include_peers"]

        chat_ids = [chat.get("channel_id", chat.get("chat_id", chat.get("user_id", ""))) for chat in peers]
        saved_chat_ids = [chat.get('_id') for chat in conn.get_chats()]
        chats_to_invalidate = list(set(saved_chat_ids) - set(chat_ids))
        conn.invalidate_chats(chats_to_invalidate)

        # chats_to_add = list(set(chat_ids) - set(saved_chat_ids))
        chat_infos_to_add = []
        for _id in chat_ids:
            try:
                ent = await client.get_entity(_id)
            # sometimes it thinks that _id is an id of user for some reason, in that case we need to cast it explicitly
            except ValueError:
                ent = await client.get_entity(telethon.tl.types.PeerChannel(_id))
            chat_infos_to_add.append({
                '_id': _id,
                'type': get_chat_type(ent),
                'title': ent.title,
                'username': get_chat_username(ent),
            })
        conn.add_chats(chat_infos_to_add)
        # print('Chats updated')
        logging.info(f'Chats updated. New chats added: {len(chat_infos_to_add)}. Chats invalidated: {len(chats_to_invalidate)}')


    def msg_hash(text):
        return md5(text.encode('utf-8')).hexdigest()


    async def main():
        conn = Connection(host, port, db_name)
        # await update_chats(conn)
        hour_cutoff = hours_to_scrape
        date_cutoff = datetime.datetime.now() - datetime.timedelta(hours=hour_cutoff)
        # chat_ids = [x['_id'] for x in conn.get_active_chats()]
        chats = conn.get_active_chats()

        for chat in chats:
            # chat_info = conn.get_chat_info(chat['_id'])
            last_analyzed_id = chat.get('last_analyzed_id', 0)
            # print('getting ' + str(chat_info.get('title')) + ' history')
            try:
                # should be 5000 or last_analyzed_id == 0
                if last_analyzed_id < (id_cutoff := await get_last_message(chat['_id']) - 5000):
                    last_analyzed_id = id_cutoff
            except (telethon.errors.RPCError, telethon.errors.rpcerrorlist.ChatInvalidError, ValueError) as e:
                # try InviteToChannelRequest to get into channel
                # TODO log it properly, mark chat as neede work
                # TODO this is only relevant if chats are passed by id, not read from telegram
                logging.critical("Found error %s", str(e))
                continue
            else:
                messages_hashes_seen = []
                async for message in client.iter_messages(chat['_id'],
                                                          min_id=last_analyzed_id,
                                                          reverse=True):
                    last_analyzed_id = message.id
                    keyw, exc_keyw = filters.BuyOrder.apply(message.text)
                    if message.date.replace(tzinfo=None) > date_cutoff:
                        if keyw:
                            _hash = msg_hash(message.text)
                            if _hash in messages_hashes_seen:
                                continue
                            else:
                                messages_hashes_seen.append(_hash)
                            if exc_keyw:
                                # print("Found message with hash " + _hash + ":\r\n" + reindent(message.text, 4) + "\r\n"
                                #       + "With keywords : " + str(keyw) + "\r\n"
                                #       + "Message excluded because of keywords: " + str(exc_keyw) + "\r\n")
                                if dbg_mode:
                                    logging.info("Excluded message in chat %s:\r\n"
                                                 + "%s\r\n"
                                                 + "With keywords : %s\n"
                                                 + "Message excluded because of keywords: %s\n",
                                                 get_chat_title(message.chat), reindent(message.text, 4), str(keyw), str(exc_keyw))
                                continue
                            # chat = await client.get_entity(message.peer_id)
                            c_type = get_chat_type(message.chat)
                            c_name = get_chat_title(message.chat)
                            try:
                                # print(message.from_id)
                                # print(message.input_sender)
                                # print(message.peer_id)
                                # print(message.sender)
                                # print(message.sender_id)
                                # print(message.to_id)
                                if message.from_id:
                                    users = await client.get_participants(message.from_id)
                                    username = get_username(users[0])
                                    full_name = get_full_name(users[0])
                                else:
                                    username = [chat['title']]
                                    full_name = chat['title']
                            except Exception as e:
                                logging.critical(f'''сломалося
                                                    peer_id {message.peer_id}
                                                    chat {chat}
                                                    chat_type {c_type}
                                                    chat_type {c_name}
                                                    from_id {message.from_id}
                                                    message_id {message.id}
                                                    message_text {message.text}''')
                                raise e

                            ad_info = conn.get_ad_info(username, _hash)
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
                                ad.set_date(message.date)
                                ad.set_original_chat(c_type, chat['_id'], c_name)
                                ad.set_author(full_name, username)
                                ad.set_message_id(message.id)
                                ad.open_status()
                            else:
                                # print('Found new message ' + str(message.id), c_name, str(message.date) + ':\r\n' +
                                #       reindent(message.text, 8))
                                # print("Keywords extracted : " + str(keyw) + '\r\n\r\n')
                                logging.info('Added message %s, %s, %s: \r\n'
                                             + '%s\r\n'
                                             + 'Keywords extracted : %s\n',
                                             str(message.id), c_name, str(message.date),
                                             reindent(message.text, 8),
                                             str(keyw))
                                bot_comm_message = await message.forward_to(-1001676301152)
                                ad = AdSlot(full_name,
                                            username,  # message.post_author?
                                            # _hash,
                                            c_type,
                                            chat['_id'],
                                            c_name,
                                            message.id,
                                            bot_comm_message.id,
                                            message.date,
                                            message.text,
                                            )
                                # text = filters.prepare_text(message.text)
                                ad.apply_secondary_filters(message.text)
                                await client.send_message(entity=-1001676301152,
                                                          message=ad.get_secondary_filters_message(),
                                                          reply_to=bot_comm_message)
                            ad.save_to_db(conn)
                conn.update_last_analyzed_id(chat['_id'], last_analyzed_id)


    client.loop.run_until_complete(main())
