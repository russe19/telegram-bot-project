from loader import bot
from telebot.types import Message


@bot.message_handler(content_types=['text'])
def hello(message):
    if message.text == 'Привет':
        mess = f'Привет, мое имя {bot.get_me().first_name}'
        bot.send_message(message.from_user.id, mess)
