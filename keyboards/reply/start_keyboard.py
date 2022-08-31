from telebot.types import ReplyKeyboardMarkup, KeyboardButton

def start_key() -> ReplyKeyboardMarkup:
    """
    Функция создает клавиатуру, в которую можно отправить одну из основных команд.
    Returns:
        markup: Клавиатура с доступными командами.

    """
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(KeyboardButton(text="Помощь"))
    markup.add(KeyboardButton(text="Список дешевых отелей"))
    markup.add(KeyboardButton(text="Список дорогих отелей"))
    markup.add(KeyboardButton(text="Список отелей по цене и расположению"))
    markup.add(KeyboardButton(text="История поиска отелей"))
    return markup