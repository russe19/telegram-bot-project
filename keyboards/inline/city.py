from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from loader import bot

def city_keyboard(message, text) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    for i in text:
        markup.add(InlineKeyboardButton(text=str(i['name']), callback_data=str(i['destinationId'])))
    bot.send_message(message.from_user.id, f"Уточните важе местоположение", reply_markup=markup)
    return markup

# @bot.callback_query_handler(func=lambda callback: callback.data)
# def callback_city_id(callback):
#     global city_id
#     city_id = callback.data
#     bot.send_message(callback.message.chat.id, f'Вы нажали {city_id}')
#     bot.answer_callback_query()

# @bot.callback_query_handler(func=lambda callback: callback.data)
# def callback_city_id(callback):
#     global city_id
#     city_id = callback.data
#     bot.send_message(callback.message.chat.id, f'Вы нажали {city_id}')
#     bot.answer_callback_query()
