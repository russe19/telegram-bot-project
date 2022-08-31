from telebot.types import Message

from loader import bot


@bot.message_handler(state=None)
def bot_echo(message: Message) -> None:
    """
    Эхо хендлер, в который попадают все текстовые сообщения без указанного состояния
    Args:
        message: Сообщение от пользователя, без указанного состояния.

    """
    bot.reply_to(message, "Эхо без состояния или фильтра.\nСообщение:"
                          f"{message.text}")
