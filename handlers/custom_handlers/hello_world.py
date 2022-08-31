from telebot.types import Message

from loader import bot


@bot.message_handler(commands=['hello-world'])
def start(message):
    """
    Функция в ответ на команду пользователя отправляет ему сообщение "Hello world".
    Args:
        message: Команда hello-world полученная от пользователя.

    """
    bot.send_message(message.from_user.id, "Hello world")
