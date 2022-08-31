from telebot.types import Message

from loader import bot


@bot.message_handler(regexp=r"^Привет$")
def hello(message):
    """
    Функция в ответ на приветствие пользователя овечает приветствует его и отправляет имя телеграмм бота.
    Args:
        message: Сообщение от пользователя.

    """
    text = f'Привет, мое имя {bot.get_me().first_name}'
    bot.send_message(message.from_user.id, text)
