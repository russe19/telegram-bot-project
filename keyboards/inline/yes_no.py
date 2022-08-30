from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from loader import bot

def yes_no_keyboard(message, text) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    mark_yes = InlineKeyboardButton(text='Да', callback_data='yes')
    mark_no = InlineKeyboardButton(text='Нет', callback_data='no')
    markup.add(mark_yes, mark_no)
    bot.send_message(message.from_user.id, text, reply_markup=markup)
    return markup