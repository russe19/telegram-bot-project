import re
import sqlite3

from telebot import types
from telebot.types import Message

from loader import bot


@bot.message_handler(regexp=r"^История поиска отелей$")
@bot.message_handler(commands=['history'])
def sql_history(message: Message) -> None:  # Вводим команду history
    """
    Функция позволяет получать из базы данных результаты поиска последней введенной команды.
    Args:
        message: Команда history

    """
    connect = sqlite3.connect('database/database.db')
    cursor = connect.cursor()
    cursor = connect.cursor()
    bot.send_message(message.chat.id, "Последняя запрошенная команда:")
    for max_time in cursor.execute("SELECT MAX(time) FROM data"):
        for answer in cursor.execute("SELECT * FROM data WHERE time=(?)", max_time):
            bot.send_message(message.chat.id, f"Команда: {answer[0]}\n"
                                              f"Время вызова команды: {answer[1]}\nПолученный отель: {answer[2]}")
    connect.commit()