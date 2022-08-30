from telebot.types import ReplyKeyboardMarkup, KeyboardButton

def calendar_days(mounth) -> ReplyKeyboardMarkup:
    markup = ReplyKeyboardMarkup()
    for i in mounth:
        markup.add(KeyboardButton(text=f'{i}'))
    return markup


def calendar_days(mounth) -> ReplyKeyboardMarkup:
    markup = ReplyKeyboardMarkup()
    for i in mounth:
        markup.add(KeyboardButton(text=f'{i}'))
    return markup