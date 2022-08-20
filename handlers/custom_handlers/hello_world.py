from loader import bot
from telebot.types import Message


@bot.message_handler(commands=['hello-world'])
def start(message):
    bot.send_message(message.from_user.id, "Hello world")
