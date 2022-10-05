import copy

import telebot
from time import sleep
import os
import requests
from contextlib import ExitStack
import logging

bot_token = os.getenv("KONEVOD_TOKEN")

bot = telebot.TeleBot(bot_token)

logging.basicConfig(filename='bot.log', encoding='utf-8', level=logging.INFO)


# extracts arguments from message with bot commands
def extract_arg(arg):
    return arg.split()[1:]


@bot.message_handler(commands=['post_products'])
def send_products(message):
    logging.info(f"Sending messages about products to chat with id = {message.from_user.id}")
    bot.send_message(message.from_user.id, "Сейчас завалю здесь все кроссовками")


@bot.message_handler(commands=['post_product'])
def send_product(message):
    args = extract_arg(message.text)
    if len(args) == 0:
        bot.send_message(message.from_user.id, "Не указан 1-ый аргумент - код продукта")


# Обрабатывает обычные текстовые сообщения
@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    print(message)
    if message.text == "/help":
        bot.send_message(message.from_user.id, "Напиши привет")
    elif message.text == 'Поздравить Катю':
        bot.send_message(message.chat.id, "Катя, с днём рождения!")
    else:
        bot.send_message(message.chat.id, "Я тебя не понимаю. Напиши /help.")
        pass


# send_message()
logging.info("Starting the bot")
bot.polling(none_stop=True, interval=1)
