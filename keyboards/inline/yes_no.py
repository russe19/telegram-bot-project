from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from loader import bot


def yes_no_keyboard(message, text) -> InlineKeyboardMarkup:
    """
    Функция, выводящая инлайн клавиатуру.
    Args:
        message: Сообщение от пользователя.
        text: Текст, который выводится вместе с клавиатурой.

    Returns:
        markup: Клавиатура с выбором ответа 'Да' или 'Нет'.

    """
    markup = InlineKeyboardMarkup()
    mark_yes = InlineKeyboardButton(text='Да', callback_data='yes')
    mark_no = InlineKeyboardButton(text='Нет', callback_data='no')
    markup.add(mark_yes, mark_no)
    bot.send_message(message.from_user.id, text, reply_markup=markup)
    return markup