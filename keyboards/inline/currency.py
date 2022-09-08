from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from loader import bot


def currency_keyboard(message: Message, all_currency: dict) -> InlineKeyboardMarkup:
    """
    Функция создает инлайн клавиатуру, и по введенному городу выводит группу городов для уточнения выбора.
    Args:
        message: Сообщение от пользователя.
        text: Словарь, в котором хранится информация по введенному городу.
    Returns:
        markup: Клавиатура, на которой можно выбрать определенный город.

    """
    markup = InlineKeyboardMarkup()
    for i in all_currency:
        markup.add(InlineKeyboardButton(text=str(i), callback_data=str(all_currency[i])))
    bot.send_message(message.from_user.id, f"Выберите валюту", reply_markup=markup)
    return markup