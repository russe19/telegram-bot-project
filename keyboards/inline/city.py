from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from loader import bot


def city_keyboard(message: Message, text: dict) -> InlineKeyboardMarkup:
    """
    Функция создает инлайн клавиатуру, и по введенному городу выводит группу городов для уточнения выбора.
    Args:
        message: Сообщение от пользователя.
        text: Словарь, в котором хранится информация по введенному городу.
    Returns:
        markup: Клавиатура, на которой можно выбрать определенный город.

    """
    markup = InlineKeyboardMarkup()
    for i in text:
        markup.add(InlineKeyboardButton(text=str(i['name']), callback_data=str(i['destinationId'])))
    bot.send_message(message.from_user.id, f"Уточните важе местоположение", reply_markup=markup)
    return markup


