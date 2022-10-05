import datetime
import telethon
from bson import ObjectId
from hashlib import md5

import filters
from db import Connection

status_names = ["open", "closed", "expired"]
original_chat_types = ["user", "chat", "channel"]
bot_comm_chat_id = -1001676301152


class AdSlot:
    id: ObjectId = None            # key assigned by db
    author = ''
    author_username = ''
    message_hash = None
    original_chat_type = ''
    original_chat_id = ''
    original_chat_name = ''
    message_id = ''
    bot_comm_message_id = None
    date_published = datetime.datetime(1970, 1, 1)
    status = ''
    text = ''
    secondary_filters = [
        filters.Reach,
        filters.Audience,
        filters.Category,
        filters.Stat,
    ]
    secondary_filter_params = None

    def __init__(self,
                 author,
                 author_username,
                 # message_hash,
                 original_chat_type,
                 original_chat_id,
                 original_chat_name,
                 message_id,
                 bot_comm_message_id,
                 date,
                 text,
                 status='open',
                 secondary_filter_params=None
                 ):
        self.author = author
        self.author_username = author_username
        # self.message_hash = message_hash
        self.message_hash = md5(text.encode('utf-8')).hexdigest()
        self.original_chat_type = original_chat_type
        self.original_chat_id = original_chat_id
        self.original_chat_name = original_chat_name
        self.message_id = message_id
        self.bot_comm_message_id = bot_comm_message_id
        self.date_published = date
        self.text = text
        self.status = status
        if status not in status_names:
            raise Exception(f"Status {status} is unknown, please use one of available statuses")
        if secondary_filter_params is None:
            self.secondary_filter_params = {}
        else:
            self.secondary_filter_params = secondary_filter_params

    def __repr__(self):
        return (f'{__class__.__name__}('
                f'{self.id!r}, {self.author!r})')

    # careful, does not include id
    def __iter__(self):
        # yield 'id', self.id
        yield 'author_name', self.author
        yield 'author_username', self.author_username
        yield 'message_hash', self.message_hash
        yield 'original_chat_type', self.original_chat_type
        yield 'original_chat_id', self.original_chat_id
        yield 'original_chat_name', self.original_chat_name
        yield 'message_id', self.message_id
        yield 'bot_comm_chat_id', bot_comm_chat_id
        yield 'bot_comm_message_id', self.bot_comm_message_id
        yield 'date_published', self.date_published
        yield 'text', self.text
        yield 'status', self.status
        yield 'date_updated', datetime.datetime.now()
        yield 'secondary_filter_params', self.secondary_filter_params

    def set_date(self, date):
        # TODO type heck
        self.date_published = date

    def set_author(self, author_full_name, author_username):
        self.author = author_full_name
        self.author_username = author_username

    def set_original_chat(self, original_chat_type, original_chat_id, original_chat_name):
        self.original_chat_type = original_chat_type
        self.original_chat_id = original_chat_id
        self.original_chat_name = original_chat_name

    def set_message_id(self, message_id):
        self.message_id = message_id

    def set_status(self, status):
        self.status = status

    def apply_secondary_filters(self, text):
        for filt in self.secondary_filters:
            self.secondary_filter_params = self.secondary_filter_params | filt.apply(text)

    def get_secondary_filters_message(self):
        res = ''
        for filt in self.secondary_filters:
            res += str(filt.get_text_repr(self.secondary_filter_params))
        return res

    def save_to_db(self, conn: Connection):
        if self.id is None:
            conn.upsert_collection('ads',
                                   {'author_username': self.author_username, 'message_hash': self.message_hash},
                                   dict(self)
                                   )
        else:
            conn.upsert_collection('ads', {'_id': self.id}, dict(self))

