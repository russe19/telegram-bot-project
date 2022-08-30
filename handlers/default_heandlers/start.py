from telebot.types import Message
from telebot import types
from loader import bot
from keyboards.reply.start_keyboard import start_key
import photo

media = []
@bot.message_handler(commands=['start'])
def bot_start(message: Message):
    markup = start_key()
    file = open("photo/menu.jpg", 'rb')
    media.append(types.InputMediaPhoto(media=file, caption="Добро пожаловать в главное меню!"))
    bot.send_media_group(message.from_user.id, media)
    bot.send_message(message.from_user.id, text = 'Для продолжения выберите нужную команду:', reply_markup=markup)

