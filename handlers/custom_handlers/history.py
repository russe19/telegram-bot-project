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
    with sqlite3.connect('database/database.db') as connect:
        cursor = connect.cursor()
        for i in cursor.execute("SELECT COUNT(command) FROM data"):
            if i[0] == 0:
                bot.send_message(message.chat.id, "База данных пуста")
                connect.commit()
            else:
                bot.send_message(message.chat.id, "Выводим 5 последних найденных отеля")
                for answer in cursor.execute("SELECT * FROM (SELECT * FROM data ORDER BY id DESC LIMIT 5) ORDER BY id"):
                    bot.send_message(message.chat.id, f"Команда: {answer[1]}\n"
                                                      f"Время вызова команды: {answer[2]}\nПолученный отель: {answer[3]}")
            connect.commit()
    bot.send_message(message.chat.id, "Запрос выполнен, выберете следующую команду\n"
                                               "/lowprice - список дешевых отелей\n/highprice - список дорогих отелей\n"
                                               "/bestdeal - список отелей по стоимости и расстоянию до цента\n"
                                               "/history - ответ на последний полученный запрос")