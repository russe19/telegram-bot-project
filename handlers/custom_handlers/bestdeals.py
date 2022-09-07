import calendar
import json
import re
import sqlite3
from datetime import date, datetime
from typing import Tuple

from loguru import logger
from telebot import types
from telebot.types import Message, CallbackQuery
from telegram_bot_calendar import LSTEP, DetailedTelegramCalendar

import api_requests
from database.sqlite_command import insert_db
from keyboards.inline import city, yes_no, currency, locale
from loader import bot
from states.contact_information import UserInfoState


sample_locales = {'Английский': 'en_US', 'Французский': 'fr_FR', 'Испанский': 'es_ES',
                  'Португальский': 'pt_PT', 'Немецкий': 'de_DE', 'Русский': 'ru_RU'
}

sample_currency = {'Рубль': 'RUB', 'Евро': 'EUR', 'Доллар': 'USD'}

def info(text: dict) -> Tuple[str, str, str, str, str]:
    """
    Функция предназначена для того, чтобы находить в тексте с помощью регулярных выражений
    необходимые параметры, и выводить их в ответ на запрос телеграмм бота.
    Args:
        text: Словарь полученный из модифицированного JSON-объекта, в котором содержится
            вся информация по заданному отелю.

    Returns:
        Функция возращает название отеля, улицу на которой он расположен, расстояние до центра,
            стоимость проживания за сутки и id отеля.
    """
    h_name = re.search(r"(?<='name': ')[^']+", str(text)) # Название отеля
    h_street = re.search(r"(?<='streetAddress': ')[^']+", str(text)) # Улица
    h_dist = re.search(r"(?<='distance': ')[^']+", str(text['landmarks'])) # Расстояние до центра
    h_cost = re.search(r"(?<='current': ')[^']+", str(text['ratePlan'])) # Стоимость за ночь
    h_id = (re.search(r"(?<='id': )\w+", str(text))) # ID отеля
    return h_name.group(), h_street.group(), h_dist.group(), h_cost.group(), h_id.group()

def find_photo(endpoint: str, hotel_id: str, photo_count: int) -> list:
    """
    Функция по id отеля находит определенное количество фотографий.
    Args:
        endpoint: Эндпоинт для запроса к API, чтобы найти фото необходимого отеля.
        hotel_id: ID отеля.
        photo_count: Необходимое количество фотографий.

    Returns:
        photo_list: Список с необходимым количеством фотографий по отелю.

    """
    mod_photo = api_requests.location_processing(endpoint=endpoint, hotel_id=hotel_id)
    mod_list = re.findall(r"(?<='baseUrl': ')\S+", str(mod_photo))
    photo_list = [i[:-2].format(size='z') for j, i in enumerate(mod_list) if j < photo_count]
    return photo_list


@bot.message_handler(regexp=r"^Список отелей по цене и расположению$")
@bot.message_handler(commands=['bestdeal'])
def lowprice_command(message: Message) -> None:  # Вводим команду lowprice
    """
    Функция получает команду на поиск отеля по цене и расположению от пользователя, и просит выбрать язык.
    Args:
        message: Команда полученная от пользователя

    """
    bot.set_state(message.from_user.id, UserInfoState.locale, message.chat.id)
    # bot.send_message(message.chat.id, f"Привет {message.from_user.first_name}, "
    #                                   f"введи на каком языке вы хотите вводить город")  # Вводим город
    locale.locale_keyboard(message, sample_locales)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data_low:  # Да или Нет записываем в список
        if message.text == "Список отелей по цене и расположению" or message.text == "/bestdeal":
            data_low['command'] = "bestdeal"
        data_low['time_command'] = datetime.utcfromtimestamp(int(message.date)).strftime('%Y-%m-%d %H:%M:%S')


@bot.message_handler(state=UserInfoState.low_price)
def bestdead_low_price(message: Message) -> None:  # Вводим кол_во отелей
    """
    Функция получает минимально-допустимую цену от пользователя, и просит ввести максимально-допустимую цену за отель.
    Args:
        message: Минимально-допустимая цена за отель, полученная от пользователя.

    """
    if not message.text.isdigit() or int(message.text) <= 0:
        bot.send_message(message.chat.id, 'Минимальная цена является положительным числом')
    else:
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data_low:  # Берем кол-во отелей
            data_low['low_price'] = message.text
        bot.send_message(message.chat.id, f'Введите максимальную цену для отеля')
        bot.set_state(message.from_user.id, UserInfoState.high_price, message.chat.id)


@bot.message_handler(state=UserInfoState.high_price)
def bestdead_high_price(message: Message) -> None:  # Максимальная цена
    """
    Функция получает максимально-допустимую цену от пользователя, и просит ввести минимально-допустимое расстояние от центра до отеля.
    Args:
        message: Максимально-допустимая цена за отель, полученная от пользователя.

    """
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
    """
    Функция получает минимально-допустимое расстояние от центра до отеля от пользователя, и просит ввести максимально-допустимое расстояние.
    Args:
        message: Минимально-допустимое расстояние от центра до отеля, полученное от пользователя.

    """
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data_low:  # Берем кол-во отелей
        data_low['low_dist'] = message.text
    bot.send_message(message.chat.id, f'Введите максимальное расстояние до отеля')
    bot.set_state(message.from_user.id, UserInfoState.high_dist, message.chat.id)


@bot.message_handler(state=UserInfoState.high_dist)
def bestdead_high_price(message: Message) -> None:  # Вводим кол_во отелей
    """
    Функция получает максимально-допустимое расстояние от центра до отеля от пользователя, и просит ввести выводимое в запросе необходимое количество отелей.
    Args:
        message:

    """
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data_low:  # Берем кол-во отелей
        data_low['high_dist'] = message.text
    bot.send_message(message.chat.id, f'Сколько отелей необходимо вывести в результате?')
    bot.set_state(message.from_user.id, UserInfoState.low_number_of_hotel, message.chat.id)


# @bot.message_handler(state=UserInfoState.bestdeal_result)
# def count_p(message: Message) -> None:  # Вводим необходимое кол-во фотографий
#     print(341)

def result_bestdeal(choice_photo: str, text: dict, callback: CallbackQuery, low_dist: str, high_dist: str, best_hotels: list) -> None:
    """

    Args:
        choice_photo: Ответ на то, нужно ли в конце запроса выводить фотографии, или нет.
        text: Список, полученный из запроса к API, и содержащий всю ниформацию по заданному городу.
        callback: Последний ответ от нашего телеграмм бота, необходимый для отправки ему сообщений.
        low_dist: Минимально_допустимое расстояние до отеля.
        high_dist: Максимально_допустимое расстояние до отеля.
        best_hotels: Список с отелями, которые подходят по всем заданным параметрам.

    Returns:
        best_hotels: Список с отелями, которые подходят по всем заданным параметрам.
    """
    for i in text['data']["body"]["searchResults"]["results"]:
        print(i)
        dist = re.search(r"[0-9,]+", i['landmarks'][0]['distance'])
        dist = re.sub(r",", r".", dist.group())
        if float(dist) >= float(low_dist) and float(dist) <= float(high_dist):
            best_hotels.append(i)
    return best_hotels


def best_result_photo(choice_photo: str, mod_list: list, callback: CallbackQuery) -> None:
    """
    Функция, которая в зависимости от того, нужно ли выводить фото отелей или нет, ссылает на другую функцию.
    Args:
        choice_photo: Ответ на то, нужно ли в конце запроса выводить фотографии, или нет.
        mod_list: Список, полученный из запроса к API, и содержащий всю ниформацию по заданному городу.
        callback: Последний ответ от нашего телеграмм бота, необходимый для отправки ему сообщений.

    """
    if choice_photo == 'yes':
        best_result_yes(mod_list, callback)
    else:
        best_result_no(mod_list, callback)


def best_result_no(mod_list: list, callback: CallbackQuery) -> None:
    """
    Функция, в которой формируется ответ на полученные данные, если в результате запроса не нужно выводить фотографии отеля.
    Args:
        mod_list: Список, полученный из запроса к API, и содержащий всю ниформацию по заданному городу.
        callback: Последний ответ от нашего телеграмм бота, необходимый для отправки ему сообщений.

    """
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
            cost = cost.replace(',', '')
            all_cost = int(''.join(re.findall(r"[\d+]", cost))) * int(all_days)
            bot.send_message(callback.message.chat.id, f"Название отеля: {name}\nУлица: {street}\n"
                                              f"Расстояние до центра: {dist}\nСтоимость: {cost}\n"
                                                       f"Общая стоимость {all_cost} {data_low['currency']}\n"
                                                       f"Ссылка на отель: https://hotels.com/ho{id_hotel}")
            hotels.append(name)
            count += 1
    if count == 0:
        bot.send_message(callback.message.chat.id, f"К сожалению по вашеву запросу не найдены отели")
    elif count < number_of_hotels:
        bot.send_message(callback.message.chat.id, f"К сожалению по вашеву запросу не найдено необходимое кол-во отелей")
    bot.send_message(callback.message.chat.id, "Запрос выполнен, выберете следующую команду\n"
                                               "/lowprice - список дешевых отелей\n/highprice - список дорогих отелей\n"
                                               "/bestdeal - список отелей по стоимости и расстоянию до цента\n"
                                               "/history - ответ на последний полученный запрос")
    insert_db(command, time, hotels)


def best_result_yes(mod_list: list, callback: CallbackQuery) -> None:
    """
    Функция, в которой формируется ответ на полученные данные, если в результате запроса нужно выводить фотографии отеля.
    Args:
        mod_list: Список, полученный из запроса к API, и содержащий всю ниформацию по заданному городу.
        callback: Последний ответ от нашего телеграмм бота, необходимый для отправки ему сообщений.

    Returns:

    """
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
            all_cost = int(''.join(re.findall(r"[\d+]", cost))) * int(all_days)
            text = f"Название отеля: {name}\nУлица: {street}\n" \
                   f"Расстояние до центра: {dist}\nСтоимость: {cost}\n" \
                   f"Общая стоимость {all_cost} {data_low['currency']}\n" \
                   f"Ссылка на отель: https://hotels.com/ho{id_hotel}"
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
    bot.send_message(callback.message.chat.id, "Запрос выполнен, выберете следующую команду\n"
                                               "/lowprice - список дешевых отелей\n/highprice - список дорогих отелей\n"
                                               "/bestdeal - список отелей по стоимости и расстоянию до цента\n"
                                               "/history - ответ на последний полученный запрос")
    insert_db(command, time, hotels)