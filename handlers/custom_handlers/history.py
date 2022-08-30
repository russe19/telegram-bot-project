from keyboards.reply.contact import request_contact
from keyboards.inline import city, yes_no
from loader import bot
from states.contact_information import UserInfoState
from telebot.types import Message
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from telebot import types
import api_requests
import re
import json
import calendar
import sqlite3
from datetime import datetime, date
from database.sqlite_command import sqlite
from loguru import logger

@bot.message_handler(regexp=r"^История поиска отелей$")
@bot.message_handler(commands=['history'])
def lowprice_command(message: Message) -> None:  # Вводим команду history
    connect = sqlite3.connect('database/database.db')
    cursor = connect.cursor()
    bot.send_message(message.chat.id, "Последняя запрошенная команда:")
    for max_time in cursor.execute("SELECT MAX(time) FROM data"):
        for answer in cursor.execute("SELECT * FROM data WHERE time=(?)", max_time):
            bot.send_message(message.chat.id, f"Команда: {answer[0]}\n"
                                              f"Время вызова команды: {answer[1]}\nПолученный отель: {answer[2]}")
