from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from loader import bot


def locale_keyboard(message: Message, all_locale: dict) -> InlineKeyboardMarkup:
    """
    Функция создает инлайн клавиатуру, и по введенному городу выводит группу городов для уточнения выбора.
    Args:
        message: Сообщение от пользователя.
        text: Словарь, в котором хранится информация по введенному городу.
    Returns:
        markup: Клавиатура, на которой можно выбрать определенный город.

    """
    markup = InlineKeyboardMarkup()
    for i in all_locale:
        markup.add(InlineKeyboardButton(text=str(i), callback_data=str(all_locale[i])))
    bot.send_message(message.from_user.id, f"Привет {message.from_user.first_name}"
                                      f", введите на каком языке вы хотите вводить город", reply_markup=markup)
    return markup