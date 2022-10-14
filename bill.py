from yoomoney import Authorize, Client, Quickpay
import datetime

import db
from db import Connection

token = '4100117978266424.0089111004576F83E9572E3188BFDC5A9BF965150F46F58A26E57E3A51F09775F7FA70215A58EAE1FFE9794407A2799D2C111F01D5C1DF31FFEC9135AAE877E08F6404B9E1B80ACA4A4077CAF2C87C75CD328B3B53513195225C03AD6D64A70DE2764BF26DECA70B733A29D56EE850D837511B13E8A538F37072DF9655E53188'


# You have to follow link and issue permanent token
def get_temp_token():
    return Authorize(
          client_id="83E59817B93C4B2ECE6D4F80DADEABB4D7E8900756D8156DC78FA2C71090921B",
          redirect_uri="https://t.me/AdSlotBot",
          scope=["account-info",
                 "operation-history",
                 "operation-details",
                 "incoming-transfers",
                 "payment-p2p",
                 "payment-shop",
                 ]
          )


def print_account_info():
    client = Client(token)
    user = client.account_info()
    print("Account number:", user.account)
    print("Account balance:", user.balance)
    print("Account currency code in ISO 4217 format:", user.currency)
    print("Account status:", user.account_status)
    print("Account type:", user.account_type)
    print("Extended balance information:")


def get_new_3_days_bill(user_id):
    return get_new_bill(str(user_id) + "_3d", 2)


def get_new_week_bill(user_id):
    return get_new_bill(str(user_id) + "_1w", 5)


def get_new_month_bill(user_id):
    return get_new_bill(str(user_id) + "_1m", 10)


def get_new_bill(label, price):
    quickpay = Quickpay(
                receiver="4100117978266424",
                quickpay_form="shop",
                targets="Sponsor this project",
                paymentType="SB",
                sum=price,
                label=label,
                )
    # print(quickpay.base_url)
    return quickpay.redirected_url


def get_last_operation():
    client = Client(token)
    history = client.operation_history(label="a1b2c3d4e5")
    print("List of operations:")
    print("Next page starts with: ", history.next_record)
    for operation in history.operations:
        print()
        print("Operation:",operation.operation_id)
        print("\tStatus     -->", operation.status)
        print("\tDatetime   -->", operation.datetime)
        print("\tTitle      -->", operation.title)
        print("\tPattern id -->", operation.pattern_id)
        print("\tDirection  -->", operation.direction)
        print("\tAmount     -->", operation.amount)
        print("\tLabel      -->", operation.label)
        print("\tType       -->", operation.type)


def get_new_operations(from_date, span_info=False):
    client = Client(token)
    # from_date has about 4 hours offset for some reason
    history = client.operation_history(from_date=from_date)
    if span_info:
        print("List of operations:")
        # TODO запрос возвращает данные посранично, надо проходиться по всем страницами, чтобы вытащить операции
        #  начало следующей тсраницы записано в history.next_record
        print("Next page starts with: ", history.next_record)
        for operation in history.operations:
            print()
            print("Operation:", operation.operation_id)
            print("\tStatus     -->", operation.status)
            print("\tDatetime   -->", operation.datetime)
            print("\tTitle      -->", operation.title)
            print("\tPattern id -->", operation.pattern_id)
            print("\tDirection  -->", operation.direction)
            print("\tAmount     -->", operation.amount)
            print("\tLabel      -->", operation.label)
            print("\tType       -->", operation.type)
    return history.operations


def add_trial_period(conn: Connection, user_id):
    conn.add_bill_period(user_id, 'TRIAL', '3d')
    conn.permit_user(user_id)




# get_bill()
# get_new_operations(datetime.datetime.strptime('2022/09/25 13:00:00', '%Y/%m/%d %H:%M:%S'), True)
# get_last_operations(datetime.datetime.now() - datetime.timedelta(days=1))
# get_new_operations(1) #717418205202002040
# print(datetime.datetime.now() - datetime.timedelta(days=1))
# conn = db.Connection()
# poll_yoomoney_operations(conn)




# get_bill()
# get_last_operation()