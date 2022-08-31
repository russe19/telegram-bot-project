from telebot import types
from telebot.types import Message

from keyboards.reply.start_keyboard import start_key
from loader import bot

media = []
@bot.message_handler(commands=['start'])
def bot_start(message: Message) -> None:
    """
    Функция начала работы телеграмм бота, которая выводит клавиатуру с доступными командами.
    Args:
        message: Команда start от пользователя.

    """
    markup = start_key()
    bot.send_message(message.from_user.id, text = 'Добро пожаловать в главное меню!\nДля продолжения выберите нужную команду:', reply_markup=markup)

