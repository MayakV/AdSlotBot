from pymongo import MongoClient, collection
from dateutil.relativedelta import relativedelta
import datetime

# TODO make it database specific, in case test and prod databases have
#  different table names or something
collection_names = {
    'ads': 'ads',
    'chats': 'chats',
    'user_filters': 'user_filters',
    'users': 'users',
    'bills': 'bills',
    'bill_periods': 'bill_periods',
}


class Connection:
    db: collection

    def __init__(self, host_name, port, db_name):
        client = MongoClient(host_name, port)
        self.db = client[db_name]

    def get_collection(self, col_name: str):
        if col_name in collection_names:
            collect = self.db[collection_names[col_name]]
            return collect
        else:
            raise ValueError("Wrong table name")

    def get_chats(self):
        col = self.get_collection(collection_names['chats'])
        return list(col.find())

    def get_active_chats(self):
        col = self.get_collection(collection_names['chats'])
        return list(col.find({'status': 'active'}))

    def get_chat_info(self, chat_id):
        col = self.get_collection(collection_names['chats'])
        chat_info = list(col.find({'_id': chat_id}))
        if chat_info:
            return chat_info[0]
        return {}

    def get_chat_infos(self, chat_ids):
        col = self.get_collection(collection_names['chats'])
        chat_infos = list(col.find({'chat_id': {'$in': chat_ids}}))
        if chat_infos:
            return chat_infos
        return []

    def add_chat(self, _id, type='', title='', username=''):
        col = self.get_collection(collection_names['chats'])
        col.update_one({'_id': _id,
                        'status': {'$ne': 'manually disabled'}},
                       {'$set': {
                           'title': title,
                           'username': username,
                           'type': type,
                           'status': 'active',
                        },
                        '$setOnInsert': {
                               'last_analyzed_id': 0,
                               'date_added': datetime.datetime.now(),
                               'last_status_change': datetime.datetime.now(),
                        }
                       },
                       upsert=True)

    def add_chats(self, chat_infos: list):
        if chat_infos:
            for chat in chat_infos:
                self.add_chat(chat["_id"], chat["type"], chat["title"], chat["username"])

    def invalidate_chats(self, chat_ids: list):
        col = self.get_collection(collection_names['chats'])
        col.update_many({'_id': {'$in': chat_ids}},
                        {'$set': {'status': 'expired'}})

    def update_last_analyzed_id(self, chat_id, last_analyzed_id):
        self.upsert_collection(collection_names['chats'],
                               {'chat_id': chat_id},
                               {'last_analyzed_id': last_analyzed_id})

    def upsert_collection(self, col_name: str, filt: dict, record: dict):
        col = self.get_collection(col_name)
        col.update_one(filt, {'$set': record}, upsert=True)

    def get_open_ads(self):
        col = self.get_collection('ads')
        cur = col.find({'status': 'open'})
        return list(cur)

    def get_ad_info(self, author_username='', message_hash='', bot_comm_id=0):
        col = self.get_collection(collection_names['ads'])
        if message_hash:
            ad = col.find({'message_hash': message_hash})
        elif bot_comm_id:
            ad = col.find({'bot_comm_message_id': bot_comm_id})
        else:
            return None  # raise error?
        ads_info = list(ad)
        if ads_info:
            ad_info = ads_info[0]
            return ad_info
        else:
            return None

    def update_expired_ads(self, time_to_expire: datetime.timedelta):
        col = self.get_collection(collection_names['ads'])
        # expired_ads = list(col.find({'date_published': {'$lt': datetime.datetime.now() - time_to_expire}}))
        # ad_ids = [x['_id'] for x in expired_ads]
        result = col.update_many({'date_published': {'$lt': datetime.datetime.now() - time_to_expire}},
                        {'$set': {'status': 'expired'}}
                        )
        return result.modified_count


    def check_ad_exists(self, author_username, message_hash):
        if self.get_ad_info(author_username, message_hash):
            return True
        return False

    def invalidate_ad(self, _hash):
        col = self.db['ads']
        if _hash:
            col.update_one({'message_hash': _hash}, {'$set': {'status': 'invalidated'}})

    def delete_ad(self, _hash):
        col = self.db['ads']
        if _hash:
            col.delete_one({'message_hash': _hash})

    def create_user(self, user_id, username, status, date):
        col = self.db['users']
        col.insert_one({'user_id': int(user_id),
                        'username': username,
                        'payment_status': status,
                        'join_date': date})

    def create_new_user(self, user_id, username):
        self.create_user(int(user_id), username, 'new', datetime.datetime.now())

    def delete_user(self, user_id):
        col = self.db['users']
        col.delete_one({'user_id': user_id})

    def get_user(self, user_id):
        col = self.db['users']
        cur = col.find({'user_id': user_id})
        if l := list(cur):
            return l[0]
        else:
            return None

    def permit_user(self, user_id):
        col = self.get_collection(collection_names['users'])
        col.update_one({'user_id': int(user_id)},
                       {'$set': {'payment_status': 'confirmed'}},
                       # "$setOnInsert": {'user_id': user_id, 'join_date': datetime.datetime.now()
                       )  # upsert=True

    def update_expired_users(self):
        bp = self.get_collection(collection_names['bill_periods'])
        # expired_bill_periods = list(bp.find({'valid_to': {'$lt': datetime.datetime.now()}}))
        # Wrong, it jast adds msx_date attributes
        # expired_bill_periods = list(bp.aggregate([{
        #     '$setWindowFields': {
        #         'partitionBy': '$user_id',
        #         'sortBy': {'valid_to': -1},
        #         'output': {
        #             # 'user_id': '$user_id',
        #             'max_date': {
        #                 '$max': '$valid_to',
        #                 'window': {
        #                     'documents': ['unbounded', 'current']
        #                 }
        #             }
        #         }
        #     }
        # }]))
        users = self.get_collection(collection_names['users'])
        paid_users = [x['user_id'] for x in users.find({'payment_status': 'confirmed'})]
        bill_periods = list(bp.aggregate([{
            '$match': {
                'user_id': {'$in': paid_users}
            }
        }, {
            '$group': {
                '_id': '$user_id',
                'max_date': {'$max': '$valid_to'}
            }
        }]))

        expired_users = filter(lambda x: x['max_date'] < datetime.datetime.now(), bill_periods)

        user_ids = [x['user_id'] for x in expired_users]
        if user_ids:
            users = self.get_collection(collection_names['users'])
            users.update_many({'user_id': {'$in': user_ids}},
                              {'$set': {'payment_status': 'expired'}}
                              )
            return user_ids
        else:
            return []

    def get_bill(self, bill_id):
        col = self.get_collection(collection_names['bills'])
        return col.find_one({'id': bill_id})

    def get_last_bill_date(self):
        col = self.get_collection(collection_names['bills'])
        if bills := list(col.find().sort('_id', -1)):
            return bills[0]["bill_date"]
        else:
            return None

    def save_bill(self, bill_id, user_id, bill_date, period, amount):
        col = self.get_collection(collection_names['bills'])
        col.insert_one({'id': bill_id, 'user_id': user_id, 'bill_date': bill_date,
                        'period': period, 'amount': amount})

    def add_bill_period(self, user_id, bill_id, period_length):
        col = self.get_collection(collection_names['bill_periods'])
        periods = list(col.find({'user_id': user_id}).sort('_id', -1))
        now = datetime.datetime.now()

        days = 0
        weeks = 0
        months = 0
        if period_length and len(period_length) == 2:
            count, unit = period_length
            if unit == 'd':
                days = int(count)
            elif unit == 'w':
                weeks = int(count)
            elif unit == 'm':
                months = int(count)
            else:
                return  # raise error?
        else:
            return  # raise errror?
        period_length_dt = relativedelta(days=days, weeks=weeks, months=months)

        if periods:
            last_period = periods[0]
            if now > last_period['valid_to']:
                valid_from = now
                valid_to = now + period_length_dt
            else:
                valid_from = last_period['valid_to']
                valid_to = last_period['valid_to'] + period_length_dt
        else:
            valid_from = now,
            valid_to = now + period_length_dt
        col.insert_one({'user_id': user_id,
                        'bill_id': bill_id,
                        'valid_from': valid_from,
                        'valid_to': valid_to})

    # for testing only
    def clear_user_bill_history(self, user_id):
        col = self.get_collection(collection_names['bill_periods'])
        col.delete_many({'user_id': user_id})

    def get_last_bill(self, user_id):
        col = self.get_collection(collection_names['bill_periods'])
        bills = list(col.find({'user_id': user_id}).sort('valid_to', -1))
        if bills:
            return bills[0]
        else:
            return None

    def user_trial_activated(self, user_id):
        col = self.get_collection(collection_names['bill_periods'])
        trials = list(col.find({'user_id': user_id, 'bill_id': 'TRIAL'}))
        if trials:
            return True
        else:
            return False

    def get_user_filter(self, user_id, filter_type='all'):
        col = self.get_collection('user_filters')
        if filter_type == 'all':
            return list(col.find({"user_id": user_id}))
        else:
            if l := list(col.find({"user_id": user_id, 'filter_type': filter_type})):
                return l[:1]  # to ensure there is nor error if there are two filters set by accident
            else:
                return []

    def save_user_filter(self, user_id, filter_type, operand, value):
        self.upsert_collection(collection_names['user_filters'],
                               {'user_id': user_id, 'filter_type': filter_type},
                               {'operand': operand, 'value': value}
                               )

    def delete_user_filter(self, user_id, filter_type):
        col = self.get_collection('user_filters')
        col.delete_one({'user_id': user_id, 'filter_type': filter_type})

    def clear_user_filters(self, user_id):
        col = self.get_collection('user_filters')
        col.delete_many({'user_id': user_id})
