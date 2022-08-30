from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def request() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Начать выполнение программы"))
    return keyboard