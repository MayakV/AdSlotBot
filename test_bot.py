import copy

import telebot
from time import sleep
import os
import requests
from contextlib import ExitStack
import logging
import db
import user_filters
import bill
import datetime

bot_token = os.getenv("AdSlot_TOKEN")

bot = telebot.TeleBot(bot_token)

# logging.basicConfig(filename='bot.log', encoding='utf-8', level=logging.INFO)

conn = db.Connection()

bot_comm_chat_id = -1001676301152

customizable_filters = [
    user_filters.Category,
    user_filters.Reach,
    user_filters.Audience,
    user_filters.Stat,
]


def is_authorized(conn, user_id):
    user_info = conn.get_user(user_id)
    if user_info:
        if user_info['payment_status'] == 'confirmed':
            return True
        else:
            return False
    else:
        return False


def check_authorization(conn, user_id, username):
    if is_authorized(conn, user_id):
        return True
    elif conn.get_user(user_id) is None:
        welcome_new_user(user_id, username)
        return False
    else:
        trial_text = ''
        bot.send_message(user_id, "Пользователь не активирован\r\n"
                                  "Пожалуйста, воспользуйтесь командой /subscription чтобы продлить подписку")
        return False


def gen_filter_markup():
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row_width = 2
    for filt in customizable_filters:
        markup.add(telebot.types.InlineKeyboardButton(filt.f_type.title(), callback_data="filt_operand " + filt.f_type))
    return markup


def gen_filter_operands_markup(_filter):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row_width = 2
    for operand, _help in _filter.operand_help.items():
        markup.add(telebot.types.InlineKeyboardButton(_help.text,
                                                      callback_data="filt_value " + _filter.f_type + " " + operand))
    return markup


def gen_subscription_markup(trial_activated):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row_width = 2
    if not trial_activated:
        markup.add(telebot.types.InlineKeyboardButton('Активировать пробный период', callback_data="subscribe trial"))
    markup.add(telebot.types.InlineKeyboardButton('3 дня', callback_data="subscribe 3d"))
    markup.add(telebot.types.InlineKeyboardButton('Неделю', callback_data="subscribe 1w"))
    markup.add(telebot.types.InlineKeyboardButton('Месяц', callback_data="subscribe 1m"))
    return markup


def welcome_new_user(user_id, username):
    conn.create_new_user(user_id, username)
    pay_url = bill.get_new_bill(user_id)

    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton('Активировать пробный период',
                                                  callback_data="activate_trial"))
    bot.send_message(user_id,
                     "Добро пожаловать в бот! Бот помогает в поиске заявок на покупку рекламы в телеграм каналах.\r\n"
                     "Для продолжения работы предусмотрен бесплатный пробный период - 3 дня. После окончания пробного "
                     "периода, доступ предоставляется по подписке. "
                     "Оформить подписку можно воспользовавшись командой /subscription".format(url=pay_url),
                     reply_markup=markup)
    

@bot.message_handler(commands=['start'])
def welcome_message(message):
    if message.chat.type == "private":
        welcome_new_user(message.chat.id, message.chat.username)


@bot.callback_query_handler(func=lambda call: call.data.startswith('activate_trial'))
def activate_trial(call):
    if call.message.chat.type == "private":
        if conn.user_trial_activated(call.message.chat.id):
            bot.send_message(call.message.chat.id,
                             "Пробный период уже был активирован, его нельзя активировать повторно")
        else:
            bill.add_trial_period(conn, call.message.chat.id)
            conn.permit_user(call.message.chat.id)
            bot.send_message(call.message.chat.id,
                             "Для Вас активирован пробный период в 3 дня. Дата окончания: "
                             + (datetime.datetime.now() + datetime.timedelta(days=3)).strftime('%d/%m/%Y %H:%M')
                             + " по МСК")  # TODO сейчас время не по мск


@bot.message_handler(commands=['help', 'start'])
def get_help(message):
    if message.chat.type == "private" and check_authorization(conn, message.chat.id, message.chat.username):
        print(str(datetime.datetime.now()) + " Sending help to " + str(message.chat.id)
              + " " + str(message.chat.username)
              + " " + str(message.chat.first_name)
              + " " + str(message.chat.last_name))
        bot.send_message(message.chat.id,
                         "Список комманд бота:\r\n\r\n"
                         "/search - поиск заявок на покупку по настроенному фильтру\r\n"
                         "/filters - просмотр настроек фильтра\r\n" 
                         "/changefilter - настройка фильтров\r\n"
                         "/clearfilters - очистить все фильтры\r\n"                         
                         "/subscription - просмотр времени до окончания подписки, продление подписки"
                         )


@bot.message_handler(commands=['subscription'])
def print_subscription(message):
    if message.chat.type == "private":
        print(f'{str(datetime.datetime.now())} Sending subscription info to {str(message.chat.id)} '
              f'{str(message.chat.username)} {str(message.chat.first_name)} {str(message.chat.last_name)}')
        b = conn.get_last_bill(message.chat.id)
        if b:
            sub_text = f"Дата окончания подписки: " \
                       f"{b['valid_to'].strftime('%d/%m/%Y %H:%M')}" \
                       f" по МСК\r\n\r\n"  # TODO сейчас время не по мск"
        else:
            sub_text = f"Ваша подписка истекла\r\n\r\n"
        bot.send_message(message.chat.id,
                         sub_text
                         + f"Ниже Вы можете продлить подписку на: ",
                         reply_markup=gen_subscription_markup(conn.user_trial_activated(message.chat.id))
                         )


@bot.callback_query_handler(func=lambda call: call.data.startswith('subscribe'))
def print_subscribtion_link(call):
    if call.message.chat.type == "private":
        print(f"{datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')} Sending subscription link to {str(call.message.chat.id)} "
              f"{call.message.chat.username} {call.message.chat.first_name} {call.message.chat.last_name}: {call.data}")
        if len(params := call.data.split(' ')) < 2 or len(params) > 2:
            return  # raise ValueError("Wrong number of arguments in callback, callback data provided: '" + call.data + "'")
        else:
            _, period = params
        if period == 'trial':
            activate_trial(call)
            return
        elif period == '3d':
            period_text = '3 дня'
            pay_url = bill.get_new_3_days_bill(call.message.chat.id)
        elif period == '1w':
            period_text = 'неделю'
            pay_url = bill.get_new_week_bill(call.message.chat.id)
        elif period == '1m':
            period_text = 'месяц'
            pay_url = bill.get_new_month_bill(call.message.chat.id)
        else:
            return # raise error?

        bot.send_message(call.message.chat.id,
                         "Вы можете оплатите подписку на {period} по [ссылке]({url})".format(period=period_text, url=pay_url),
                         parse_mode='MarkdownV2')


@bot.message_handler(commands=['filters'])
def print_user_filters(message):
    if message.chat.type == "private" and check_authorization(conn, message.chat.id, message.chat.username):
        print(str(datetime.datetime.now()) + " Sending filters to " + str(message.chat.username)
              + " " + str(message.chat.first_name)
              + " " + str(message.chat.last_name))
        text = ''
        for _filter in customizable_filters:
            s = _filter.get_string(conn, message.chat.id)
            text += s
        print(text)
        bot.send_message(message.chat.id, text)


@bot.message_handler(commands=['clearfilters'])
def clear_user_filters(message):
    if message.chat.type == "private" and check_authorization(conn, message.chat.id, message.chat.username):
        conn.clear_user_filters(message.chat.id)
        print(str(datetime.datetime.now()) + " Clearing filters for " + str(message.chat.username)
              + " " + str(message.chat.first_name)
              + " " + str(message.chat.last_name))
        bot.send_message(message.chat.id, "Фильтры удалены")


@bot.callback_query_handler(func=lambda call: call.data.startswith('filt_operand '))
def choose_filter_action(call):
    if call.message.chat.type == "private":
        print("got callbakc :" + call.data)
        if len(params := call.data.split(' ')) < 2 or len(params) > 2:
            return  # raise ValueError("Wrong number of arguments in callback, callback data provided: '" + call.data + "'")
        else:
            _, filter_type = params
        _filter = next((filt for filt in customizable_filters if filt.f_type == filter_type), None)
        markup = gen_filter_operands_markup(_filter)

        bot.send_message(call.message.chat.id,
                         _filter.help_text + "\r\nТекущее значение фильтра:\r\n" + _filter.get_string(conn, call.message.chat.id) +
                         "\r\nВыберите действие для фильтра",
                         reply_markup=markup)


# Подумать, может оставить это второй опцией изменения фильтра типа для опытных

# @bot.message_handler(commands=['changefilter'])
# def set_user_filter(message):
#     if message.chat.type == "private" and check_authorization(conn, message.chat.id):
#         print("Changing filter for " + str(message.chat.username)
#               + " " + str(message.chat.first_name)
#               + " " + str(message.chat.last_name)
#               + ": " + str(message.text.split()))
#         if len(args := message.text.split()) < 3:
#             bot.send_message(message.chat.id, "Недостаточно аргументов, пожалуйста, "
#                                               "воспользуйтесь командой /help уточнения синтаксиса команды")
#             return
#         filter_type = args[1:2][0]
#         if filter_type:
#             # what does it do?
#             _filter = next((filt for filt in customizable_filters if filt.f_type == filter_type), None)
#             if _filter:
#                 reply = _filter.modify_filter(conn, message.chat.id, *message.text.split()[2:4])
#                 bot.send_message(message.chat.id, reply)
#             else:
#                 bot.send_message(message.chat.id, 'Указанного фильтра не существует. \r\nВоспользуйтесь /помощь')
#         else:
#             bot.send_message(message.chat.id, 'Тип фильтра не указан. Воспользуйтесь /помощь')

@bot.message_handler(commands=['changefilter'])
def set_user_filter(message):
    if message.chat.type == "private" and check_authorization(conn, message.chat.id, message.chat.username):
        print(str(datetime.datetime.now()) + " Changing filter for " + str(message.chat.username)
              + " " + str(message.chat.first_name)
              + " " + str(message.chat.last_name)
              + ": " + str(message.text.split()))
        bot.send_message(message.from_user.id,
                         "Выберите фильтр, который вы хотели бы изменить",
                         reply_markup=gen_filter_markup())


@bot.callback_query_handler(func=lambda call: call.data.startswith('filt_operand '))
def choose_filter_action(call):
    if call.message.chat.type == "private":
        print("got callbakc :" + call.data)
        if len(params := call.data.split(' ')) < 2 or len(params) > 2:
            return  # raise ValueError("Wrong number of arguments in callback, callback data provided: '" + call.data + "'")
        else:
            _, filter_type = params
        _filter = next((filt for filt in customizable_filters if filt.f_type == filter_type), None)
        markup = gen_filter_operands_markup(_filter)

        bot.send_message(call.message.chat.id,
                         _filter.help_text + "\r\nТекущее значение фильтра:\r\n" + _filter.get_string(conn, call.message.chat.id) +
                         "\r\nВыберите действие для фильтра",
                         reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('filt_value '))
def choose_filter_value(call):
    if call.message.chat.type == "private":
        print("got callback :" + call.data)
        if len(params := call.data.split(' ')) < 3 or len(params) > 3:
            return  # raise ValueError("Wrong number of arguments in callback, callback data provided: '" + call.data + "'")
        else:
            _, filter_type, operand = params
        _filter = next((filt for filt in customizable_filters if filt.f_type == filter_type), None)
        if _filter.operand_help[operand].number_of_args == 0:
            print("modifying filter")
            _reply = modify_filter(call.message.chat.id, _filter, operand, '')
            bot.send_message(call.message.chat.id, _reply)
        else:
            print("asking for value")
            msg = bot.send_message(call.message.chat.id,
                             "Введите новое значение для фильра:")
            bot.register_next_step_handler(msg, get_new_filter_value, _filter, operand)


def get_new_filter_value(message, _filter, operand):
    if message.chat.type == "private":
        print("got value " + message.text)
        _reply = modify_filter(message.chat.id, _filter, operand, message.text.lower())
        bot.send_message(message.chat.id, _reply)


def modify_filter(user_id, _filter, operand, value=''):
    # _filter = next((filt for filt in customizable_filters if filt.f_type == filter_type), None)
    return _filter.modify_filter(conn, user_id, operand, value)
    #                 bot.send_message(message.chat.id, reply)


@bot.message_handler(commands=['search'])
def get_ads(message):
    if message.chat.type == "private" and check_authorization(conn, message.chat.id, message.chat.username):
        print(str(datetime.datetime.now()) + " Sending ads to " + str(message.chat.username)
              + " " + str(message.chat.first_name)
              + " " + str(message.chat.last_name))
        # print("Getting ads")
        ads = conn.get_open_ads()
        for _filter in customizable_filters:
            ads = _filter.apply(conn, message.chat.id, ads)
        if ads:
            for ad in ads:
                # print('Forwarding ad')
                bot.forward_message(message.chat.id, ad['bot_comm_chat_id'], ad['bot_comm_message_id'])
        else:
            bot.send_message(message.from_user.id, "По настроенным фильтрам не найдено заявок")


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    print(message.text)
    # print(bot.retrieve_data( ))
    # bot.forward_message(536303432, 536303432, 55093)
    str(message.chat.id)
    # bot.forward_message(5615779963, 5615779963, 55093)
    if message.text == "/help":
        bot.send_message(message.from_user.id, "Напиши привет")
    elif message.text == 'Поздравить Катю':
        bot.send_message(message.chat.id, "Катя, с днём рождения!")
    elif message.text == '/get':
        print('Getting ads')

    else:
        # bot.send_message(message.chat.id, "Я тебя не понимаю. Напиши /help." + str(message.chat.id))
        pass


# send_message()
logging.info("Starting the bot")
bot.infinity_polling(interval=5)
