import datetime
import logging
import configparser
import telebot
import os

# needed to import modules below
# parent_dir = os.path.abspath(os.path.join(__file__, os.pardir, os.pardir))
# print(parent_dir)
# sys.path.insert(0, parent_dir)

import shared.db as db
import shared.user_filters as user_filters
import shared.bill as bill
import shared.AdSlot as AdSlot
from shared.filters import active_filters

configParser = configparser.RawConfigParser()
# configFilePath = os.path.join(os.path.abspath(os.path.join(__file__, os.pardir, os.pardir)), 'config',
#                               r'bot_config.txt')
configFilePath = r'bot_config.txt'
configParser.read(configFilePath)
# bot_token = os.getenv("TELEGRAM_TOKEN_PROD")
bot_token = configParser.get('General', 'Token')

telebot.apihelper.SESSION_TIME_TO_LIVE = 60 * 5
telebot.apihelper.READ_TIMEOUT = 5
bot = telebot.TeleBot(bot_token)

db_name = configParser.get('General', 'Db_name')
host = configParser.get('General', 'Host')


conn = db.Connection(host, db_name)

bot_comm_chat_id = -1001676301152

customizable_filters = [
    user_filters.Category,
    user_filters.Reach,
    user_filters.Audience,
    user_filters.Stat,
]

full_check = u'\U00002611'
empty_check = u'\U0001F532'


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
    buttons = [telebot.types.InlineKeyboardButton(f.f_type.title(), callback_data="filt_operand " + f.f_type)
               for f in customizable_filters]
    markup.add(*buttons, row_width=2)
    return markup


def gen_filter_operands_markup(_filter, values_enabled):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row_width = 2
    buttons = []
    if _filter.input_type == 'inline':
        # TODO it assumes value is list, which is not always the case, make better system
        buttons.extend(
            [telebot.types.InlineKeyboardButton(
                (full_check if val in values_enabled else empty_check) + " " + val.title(),
                callback_data="filt_value_inline "
                              + _filter.f_type
                              + " " + ('-' if val in values_enabled else '+')
                              + " " + val)
                for val in _filter.valid_values])
    for operand, _help in _filter.operand_help.items():
        if _filter.operand_help[operand].input_type in (None, 'type_in'):
            buttons.append(telebot.types.InlineKeyboardButton(_help.text,
                                                              callback_data="filt_value " + _filter.f_type + " " + operand))
        elif _filter.operand_help[operand].input_type == 'inline':
            # TODO it assumes value is list, which is not always the case, make better system
            buttons.append(telebot.types.InlineKeyboardButton
                           (_help.text,
                            callback_data="filt_value_inline " + _filter.f_type + " " + operand + " " + 'null'))
    markup.add(*buttons, row_width=2)
    return markup


def gen_subscription_markup(trial_activated):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row_width = 2
    if not trial_activated:
        markup.add(telebot.types.InlineKeyboardButton('Активировать пробный период', callback_data="subscribe trial"))
    markup.add(telebot.types.InlineKeyboardButton('3 дня', callback_data="subscribe 3d"))
    markup.add(telebot.types.InlineKeyboardButton('Неделя', callback_data="subscribe 1w"))
    markup.add(telebot.types.InlineKeyboardButton('Месяц', callback_data="subscribe 1m"))
    return markup


def welcome_new_user(user_id, username):
    conn.create_new_user(user_id, username)

    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton('Активировать пробный период',
                                                  callback_data="activate_trial"))
    bot.send_message(user_id,
                     "Вас приветствует бот! Бот помогает в поиске заявок на покупку рекламы в телеграм каналах.\r\n"
                     "Для продолжения работы предусмотрен бесплатный пробный период - 3 дня. После окончания пробного "
                     "периода, доступ предоставляется по подписке. "
                     "Оформить подписку можно воспользовавшись командой /subscription",
                     reply_markup=markup)


@bot.message_handler(commands=['start'])
def welcome_message(message):
    if message.chat.type == "private":
        if conn.get_user(message.chat.id):
            bot.send_message(message.chat.id, "Пользователь уже добавлен в систему")
        else:
            welcome_new_user(message.chat.id, message.chat.username)


@bot.callback_query_handler(func=lambda call: call.data.startswith('activate_trial'))
def activate_trial(call):
    if call.message.chat.type == "private":
        if conn.user_trial_activated(call.message.chat.id):
            bot.send_message(call.message.chat.id,
                             "Пробный период уже был использован, его нельзя активировать повторно")
        else:
            bill.add_trial_period(conn, call.message.chat.id)
            conn.permit_user(call.message.chat.id)
            bot.send_message(call.message.chat.id,
                             "Для Вас активирован пробный период в 3 дня. Дата окончания: "
                             + (datetime.datetime.now() + datetime.timedelta(days=3)).strftime('%d/%m/%Y %H:%M')
                             + " по МСК")  # TODO сейчас время не по мск


@bot.message_handler(commands=['help'])
def get_help(message):
    if message.chat.type == "private":
        print(str(datetime.datetime.now()) + " Sending help to " + str(message.chat.id)
              + " " + str(message.chat.username)
              + " " + str(message.chat.first_name)
              + " " + str(message.chat.last_name))
        bot.send_message(message.chat.id,
                         "Список комманд бота:\r\n\r\n"
                         "/search - поиск заявок на покупку по настроенному фильтру\r\n"
                         "/filters - просмотр настроек фильтров\r\n"
                         "/changefilter - настройка фильтров\r\n"
                         "/clearfilters - очистить все фильтры\r\n"
                         "/subscription - управление подпиской, позволяет активировать пробный период "
                         "или подписаться на 3 дня, неделю, месяц"
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
                         + f"Для оформления новой подписки выберите желаемый период: ",
                         reply_markup=gen_subscription_markup(conn.user_trial_activated(message.chat.id))
                         )


@bot.callback_query_handler(func=lambda call: call.data.startswith('subscribe'))
def print_subscription_link(call):
    if call.message.chat.type == "private":
        print(
            f"{datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')} Sending subscription link "
            f"to {str(call.message.chat.id)} "
            f"{call.message.chat.username} {call.message.chat.first_name} {call.message.chat.last_name}: {call.data}")
        if len(params := call.data.split(' ')) < 2 or len(params) > 2:
            # raise ValueError("Wrong number of arguments in callback, callback data provided: '" + call.data + "'")
            return
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
            return  # raise error?

        bot.send_message(call.message.chat.id,
                         "Вы можете оплатить подписку на {period} по [ссылке]({url})".format(period=period_text,
                                                                                             url=pay_url),
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


@bot.message_handler(commands=['changefilter'])
def set_user_filter(message):
    if message.chat.type == "private" and check_authorization(conn, message.chat.id, message.chat.username):
        print(str(datetime.datetime.now()) + " Changing filter for " + str(message.chat.username)
              + " " + str(message.chat.first_name)
              + " " + str(message.chat.last_name)
              + ": " + str(message.text.split()))
        bot.send_message(message.from_user.id,
                         "Выберите фильтр, который Вы хотели бы изменить",
                         reply_markup=gen_filter_markup())


@bot.callback_query_handler(func=lambda call: call.data.startswith('filt_operand '))
def choose_filter_action(call):
    if call.message.chat.type == "private":
        print("got callbakc :" + call.data)
        if len(params := call.data.split(' ')) < 2 or len(params) > 2:
            # raise ValueError("Wrong number of arguments in callback, callback data provided: '" + call.data + "'")
            return
        else:
            _, filter_type = params
        _filter = next((filt for filt in customizable_filters if filt.f_type == filter_type), None)
        if u_filter := conn.get_user_filter(call.message.chat.id, _filter.f_type):
            markup = gen_filter_operands_markup(_filter, u_filter[0].get('value', []))
        else:
            markup = gen_filter_operands_markup(_filter, [])

        if _filter.input_type == 'type_in':
            bot.send_message(call.message.chat.id,
                             _filter.help_text + "\r\nТекущее значение фильтра:\r\n"
                             + _filter.get_string(conn, call.message.chat.id) +
                             "\r\nВыберите действие для фильтра",
                             reply_markup=markup)
        elif _filter.input_type == 'inline':
            bot.send_message(call.message.chat.id,
                             _filter.help_text + "\r\n\r\nВыберите значение для фильтра",
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

@bot.callback_query_handler(func=lambda call: call.data.startswith('filt_value '))
def choose_filter_value(call):
    if call.message.chat.type == "private":
        print("got callback :" + call.data)
        if len(params := call.data.split(' ')) < 3 or len(params) > 3:
            # raise ValueError("Wrong number of arguments in callback, callback data provided: '" + call.data + "'")
            return
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
                                   "Введите новое значение для фильтра:")
            bot.register_next_step_handler(msg, get_typed_filter_value, _filter, operand)


def get_typed_filter_value(message, _filter, operand):
    if message.chat.type == "private":
        print("got value " + message.text)

        _reply = modify_filter(message.chat.id, _filter, operand, message.text.lower())
        bot.send_message(message.chat.id, _reply)


@bot.callback_query_handler(func=lambda call: call.data.startswith('filt_value_inline '))
def get_inline_filter_value(call):
    if call.message.chat.type == "private":
        print("got value " + call.data)
        if len(params := call.data.split(' ')) < 4 or len(params) > 4:
            # raise ValueError("Wrong number of arguments in callback, callback data provided: '" + call.data # + "'")
            return
        else:
            _, filter_type, filter_operand, filter_value = params
            filter_value = filter_value.lower() if filter_value != 'null' else ''
        _filter = next((filt for filt in customizable_filters if filt.f_type == filter_type), None)
        # markup = call.message.reply_markup
        u_filter = conn.get_user_filter(call.message.chat.id, filter_type)
        if filter_operand == '+':
            if u_filter:
                new_values = u_filter[0]['value'] + [filter_value]
            else:
                new_values = [filter_value]
        elif filter_operand == '-':
            if filter_value and u_filter:
                new_values = u_filter[0]['value']
                new_values.remove(filter_value)
            else:
                new_values = []
        else:
            new_values = []
            # raise wrong operand?

        bot.edit_message_reply_markup(chat_id=call.message.chat.id,
                                      message_id=call.message.id,
                                      reply_markup=gen_filter_operands_markup(_filter,
                                                                              new_values
                                                                              ))

        _reply = modify_filter(call.message.chat.id, _filter, filter_operand, filter_value.lower())
        # bot.send_message(message.chat.id, _reply)


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


@bot.message_handler(content_types=['audio', 'photo', 'voice', 'video', 'document',
                                    'text', 'location', 'contact',
                                    'sticker'])  # content_types=['text']
def get_text_messages(message):
    if message.chat.type == "private":
        # print(message.text)
        # # print(bot.retrieve_data( ))
        # # bot.forward_message(536303432, 536303432, 55093)
        # str(message.chat.id)
        # # bot.forward_message(5615779963, 5615779963, 55093)
        # if message.text == "/help":
        #     bot.send_message(message.from_user.id, "Напиши привет")
        # elif message.text == 'Поздравить Катю':
        #     bot.send_message(message.chat.id, "Катя, с днём рождения!")
        # elif message.text == '/get':
        #     print('Getting ads')
        #
        # else:
        #     # bot.send_message(message.chat.id, "Я тебя не понимаю. Напиши /help." + str(message.chat.id))
        #     pass
        # u =         bot.get_chat_member('tgsale', 'Profit_is')---------------------------------------------------
        bot.send_message(message.chat.id, "Неопознанная команда. Напишите /help для вывода справки по командам")


@bot.edited_message_handler(func=lambda message: message.chat.id == bot_comm_chat_id)
def handler_function(message):
    if (ad_msg := message.reply_to_message) \
            and (message.reply_to_message.forward_from or message.reply_to_message.forward_sender_name):
        # if user.username is None:
        #     bot.edit_message_text(message.text + '\r\n\r\nПользователь удален')
        # msg_hash = AdSlot.AdSlot.calc_hash(message.text)
        if ad_info := conn.get_ad_info(bot_comm_id=ad_msg.id):
            if message.text.lower() == 'удалить':
                conn.invalidate_ad(ad_info.get('message_hash', ''))
            else:
                lines = message.text.splitlines()
                ad = AdSlot.AdSlot(ad_info.get('author_name', ''),
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
                for line in lines:
                    _type, *_ = line.split(' : ')
                    _filter = next((filt for filt in active_filters if filt.f_type == _type), None)
                    if _filter:
                        new_filter_params = _filter.get_db_repr_from_text(line)
                        ad.set_secondary_filter(new_filter_params)
                        print(_filter.f_type + " updated successfully")
                    else:
                        print('Filter unknown')
                print("Ad update successfully")
                ad.save_to_db(conn)
        else:
            print("Ad not in db")
    else:
        print('Message is a reply : ' + str(ad_msg))
        # print('Original Message is forwarded from : ' + str(user))
    # message.reply_to_message


# send_message()
logging.info("Starting the bot")
bot.infinity_polling(interval=3)
# check = [u'\U000025FB', u'\U0000274C', u'\U00002714', u'\U0001F532', u'\U0001F533', u'\U00002B1C', u'\U00002705',
#          u'\U00002611']
# check = [u'\U00002611', u'\U0001F532']
# bot.send_message(536303432, 'this ' + ', '.join(check) + ' that')
