from keyboards.reply.contact import request_contact
from keyboards.inline import city, yes_no
from loader import bot
from states.contact_information import UserInfoState
from telebot.types import Message
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from telebot import types
import api_requests
import re
import json
import calendar
import sqlite3
from datetime import datetime, date
from database.sqlite_command import sqlite
from loguru import logger
"""
Функция lowprice_search используется ближе к концу кода, она нужна чтобы по городу найти id
Функции начинающиеся на result нужны чтобы найти необходимую информацию, когда бот уже получил все
необходимые данные, сначала идет result, а зетем в зависимости от ответа на вопрос про вывод фото "Да" или "Нет" 
выполняется соответствующая функция result_no или result_yes. Пока реализовал только так)
"""


"""
Начало
"""

def info(text):
    h_name = re.search(r"(?<='name': ')[^']+", str(text))
    h_street = re.search(r"(?<='streetAddress': ')[^']+", str(text))
    h_dist = re.search(r"(?<='distance': ')[^']+", str(text['landmarks']))
    h_cost = re.search(r"(?<='current': ')[^']+", str(text['ratePlan']))
    h_id = (re.search(r"(?<='id': )\w+", str(text)))
    return h_name.group(), h_street.group(), h_dist.group(), h_cost.group(), h_id.group()


def find_photo(endpoint, hotel_id, photo_count):
    mod_photo = api_requests.location_processing(endpoint=endpoint, hotel_id=hotel_id)
    mod_list = re.findall(r"(?<='baseUrl': ')\S+", str(mod_photo))
    photo_list = [i[:-2].format(size='z') for j, i in enumerate(mod_list) if j < photo_count]
    return photo_list


@bot.message_handler(regexp=r"^Список отелей по цене и расположению$")
@bot.message_handler(commands=['bestdeal'])
def lowprice_command(message: Message) -> None:  # Вводим команду lowprice
    bot.set_state(message.from_user.id, UserInfoState.low_city, message.chat.id)
    bot.send_message(message.chat.id, f"Привет {message.from_user.first_name}, введи свой город")  # Вводим город
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data_low:  # Да или Нет записываем в список
        if message.text == "Список отелей по цене и расположению" or message.text == "/bestdeal":
            data_low['command'] = "bestdeal"
        data_low['time_command'] = datetime.utcfromtimestamp(int(message.date)).strftime('%Y-%m-%d %H:%M:%S')


@bot.message_handler(state=UserInfoState.low_price)
def bestdead_low_price(message: Message) -> None:  # Вводим кол_во отелей
    if not message.text.isdigit() or int(message.text) <= 0:
        bot.send_message(message.chat.id, 'Минимальная цена является положительным числом')
    else:
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data_low:  # Берем кол-во отелей
            data_low['low_price'] = message.text
        bot.send_message(message.chat.id, f'Введите максимальную цену для отеля')
        bot.set_state(message.from_user.id, UserInfoState.high_price, message.chat.id)


@bot.message_handler(state=UserInfoState.high_price)
def bestdead_high_price(message: Message) -> None:  # Максимальная цена
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data_low:  # Берем кол-во отелей
        data_low['high_price'] = message.text
    if not message.text.isdigit() or int(message.text) <= 0:
        bot.send_message(message.chat.id, 'Максимальная цена является положительным числом')
    elif int(message.text) <= int(data_low['low_price']):
        bot.send_message(message.chat.id, 'Максимальная цена должна быть больше минимальной')
    else:
        bot.send_message(message.chat.id, f'Введите минимальное расстояние до отеля')
        bot.set_state(message.from_user.id, UserInfoState.low_dist, message.chat.id)


@bot.message_handler(state=UserInfoState.low_dist)
def bestdead_high_price(message: Message) -> None:  # Вводим кол_во отелей
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data_low:  # Берем кол-во отелей
        data_low['low_dist'] = message.text
    bot.send_message(message.chat.id, f'Введите максимальное расстояние до отеля')
    bot.set_state(message.from_user.id, UserInfoState.high_dist, message.chat.id)


@bot.message_handler(state=UserInfoState.high_dist)
def bestdead_high_price(message: Message) -> None:  # Вводим кол_во отелей
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data_low:  # Берем кол-во отелей
        data_low['high_dist'] = message.text
    bot.send_message(message.chat.id, f'Сколько отелей необходимо вывести в результате?')
    bot.set_state(message.from_user.id, UserInfoState.low_number_of_hotel, message.chat.id)


# @bot.message_handler(state=UserInfoState.bestdeal_result)
# def count_p(message: Message) -> None:  # Вводим необходимое кол-во фотографий
#     print(341)

def result_bestdeal(choice_photo, text, callback, low_dist, high_dist, best_hotels):
    for i in text['data']["body"]["searchResults"]["results"]:
        print(i)
        dist = re.search(r"[0-9,]+", i['landmarks'][0]['distance'])
        dist = re.sub(r",", r".", dist.group())
        if float(dist) >= float(low_dist) and float(dist) <= float(high_dist):
            best_hotels.append(i)
    return best_hotels


def best_result_photo(choice_photo, mod_list, callback) -> None:
    if choice_photo == 'yes':
        best_result_yes(mod_list, callback)
    else:
        best_result_no(mod_list, callback)


def best_result_no(mod_list, callback):
    count = 0
    hotels = []
    for j in mod_list:
        print(j, '\n\n')
    with bot.retrieve_data(callback.from_user.id, callback.message.chat.id) as data_low:  # Берем кол-во отелей
        number_of_hotels, time, command = int(data_low['number_of_hotels']), data_low['time_command'], data_low['command']
        all_days = (data_low['checkout'] - data_low['checkin']).days
    for i in mod_list:
        if count < number_of_hotels:
            name, street, dist, cost, id_hotel = info(i)
            all_cost = int(cost[1:]) * int(all_days)
            bot.send_message(callback.message.chat.id, f"Название отеля: {name}\nУлица: {street}\n"
                                              f"Расстояние до центра: {dist}\nСтоимость: {cost}\n"
                                                       f"Общая стоимость ${all_cost}")
            hotels.append(name)
            count += 1
    if count == 0:
        bot.send_message(callback.message.chat.id, f"К сожалению по вашеву запросу не найдены отели")
    elif count < number_of_hotels:
        bot.send_message(callback.message.chat.id, f"К сожалению по вашеву запросу не найдено необходимое кол-во отелей")
    sqlite(command, time, hotels)


def best_result_yes(mod_list, callback):
    count = 0
    media = []
    hotels = []
    with bot.retrieve_data(callback.from_user.id, callback.message.chat.id) as data_low:  # Берем кол-во отелей
        number_of_hotels, time, command, photo_count = \
            int(data_low['number_of_hotels']), data_low['time_command'], \
            data_low['command'], int(data_low['photo_count'])
        all_days = (data_low['checkout'] - data_low['checkin']).days
    for i in mod_list:
        if count < number_of_hotels:
            name, street, dist, cost, id_hotel = info(i)
            all_cost = int(cost[1:]) * int(all_days)
            text = f"Название отеля: {name}\nУлица: {street}\n" \
                   f"Расстояние до центра: {dist}\nСтоимость: {cost}\nОбщая стоимость ${all_cost}"
            hotels.append(name)
            count += 1
            photo_list = find_photo(endpoint = 'properties/get-hotel-photos', hotel_id = id_hotel, photo_count = photo_count)
            media.append(types.InputMediaPhoto(media=photo_list[0], caption=text))
            for i_photo in photo_list[1:]:
                media.append(types.InputMediaPhoto(media=i_photo))
            bot.send_media_group(callback.from_user.id, media)
            media = []
            photo_list = []
    if count == 0:
        bot.send_message(callback.message.chat.id, f"К сожалению по вашеву запросу не найдены отели")
    elif count < number_of_hotels:
        bot.send_message(callback.message.chat.id, f"К сожалению по вашеву запросу не найдено необходимое кол-во отелей")
    sqlite(command, time, hotels)