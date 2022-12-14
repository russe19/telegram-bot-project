"""
В данном модуле реализованы функции, необходимые для получения в телеграмм боте
информации по самым дорогим и самым дешевым отелям в заданном регионе
"""

import re
import locale
from datetime import date, datetime, timedelta
from typing import Tuple

from telebot import types
from telebot.types import Message, CallbackQuery
from telegram_bot_calendar import LSTEP, DetailedTelegramCalendar

import api_requests
from database.sqlite_command import insert_db, connect_sql
from handlers.custom_handlers.bestdeals import (best_result_photo,
                                                result_bestdeal)
from keyboards.inline import city, yes_no, currency, locale
from loader import bot, logger
from states.contact_information import UserInfoState

connect_sql()

sample_locales = {'Английский': 'en_US', 'Французский': 'fr_FR', 'Испанский': 'es_ES',
                  'Португальский': 'pt_PT', 'Немецкий': 'de_DE', 'Русский': 'ru_RU'
}

sample_currency = {'Рубль': 'RUB', 'Евро': 'EUR', 'Доллар': 'USD'}

def info(text: dict, callback: CallbackQuery) -> Tuple[str, str, str, str, str]:
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
    name = re.search(r"(?<='name': ')[^']+", str(text)).group() # Название отеля
    street = 'Не указана'
    try:
        street = re.search(r"(?<='streetAddress': ')[^']+", str(text)).group() # Улица
    except AttributeError:
        logger.info("ID пользователя - {user} | У отеля {name} отсутствует атрибут 'улица'",
                    user=callback.from_user.id, name=name)
    dist = re.search(r"(?<='distance': ')[^']+", str(text['landmarks'])).group() # Расстояние до центра
    cost = re.search(r"(?<='current': ')[^']+", str(text['ratePlan'])).group() # Стоимость за ночь
    id = (re.search(r"(?<='id': )\w+", str(text))).group() # ID отеля
    return name, street, dist, cost, id

def find_photo(endpoint: str, hotel_id: str, photo_count: int, callback) -> list:
    """
    Функция по id отеля находит определенное количество фотографий.
    Args:
        endpoint: Эндпоинт для запроса к API, чтобы найти фото необходимого отеля.
        hotel_id: ID отеля.
        photo_count: Необходимое количество фотографий.

    Returns:
        photo_list: Список с необходимым количеством фотографий по отелю.

    """
    mod_photo = api_requests.location_processing(endpoint=endpoint, hotel_id=hotel_id, user = callback.from_user.id)
    mod_list = re.findall(r"(?<='baseUrl': ')\S+", str(mod_photo))
    photo_list = [i[:-2].format(size='z') for j, i in enumerate(mod_list) if j < photo_count]
    return photo_list


def result_no(mod_text: dict, callback: CallbackQuery) -> None:
    """
    Фукнция, которая стработает если мы получили всю необходимую инфориацию от пользователя, для поиска
    отеля, а так же нам не нужно получать фотографии по каждому отелю.
    Args:
        mod_text: Словарь в котором содержится вся информация по городу, в котором необходимо реализовать
            поиск отелей.
        callback: Последний ответ от нашего телеграмм бота, по которому мы будем к нему обращаться
            для отправки сообщений.

    """
    count = 0
    hotels = []
    with bot.retrieve_data(callback.from_user.id, callback.message.chat.id) as data_low:  # Берем кол-во отелей
        number_of_hotels, time, command = int(data_low['number_of_hotels']), data_low['time_command'], data_low['command']
        all_days = (data_low['checkout'] - data_low['checkin']).days
    for i in mod_text['data']["body"]["searchResults"]["results"]:
        if count < number_of_hotels:
            name, street, dist, cost, id_hotel = info(i, callback)
            all_cost = int(''.join(re.findall(r"[\d+]", cost))) * int(all_days)
            bot.send_message(callback.message.chat.id, f"Название отеля: {name}\nУлица: {street}\n"
                                              f"Расстояние до центра: {dist}\nСтоимость: {cost}\n"
                                                       f"Общая стоимость {all_cost}{data_low['currency']}\n"
                                                       f"Ссылка на отель: https://hotels.com/ho{id_hotel}")
            hotels.append(name)
            count += 1
    bot.send_message(callback.message.chat.id, "Запрос выполнен, выберете следующую команду\n"
                                               "/lowprice - список дешевых отелей\n/highprice - список дорогих отелей\n"
                                               "/bestdeal - список отелей по стоимости и расстоянию до цента\n"
                                               "/history - ответ на последний полученный запрос")
    insert_db(command, time, hotels)


def result_yes(mod_text: dict, callback: CallbackQuery) -> None:
    """
    Фукнция, которая стработает если мы получили всю необходимую инфориацию от пользователя, для поиска
    отеля, а так же нам необходимо получать фотографии по каждому отелю в определенном колличестве.
    Args:
        mod_text: Словарь в котором содержится вся информация по городу, в котором необходимо реализовать
            поиск отелей.
        callback: Последний ответ от нашего телеграмм бота, по которому мы будем к нему обращаться
            для отправки сообщений.

    """
    count = 0
    media = []
    hotels = []
    with bot.retrieve_data(callback.from_user.id, callback.message.chat.id) as data_low:
        number_of_hotels, time, command, photo_count = \
            int(data_low['number_of_hotels']), data_low['time_command'], \
            data_low['command'], int(data_low['photo_count'])
        all_days = (data_low['checkout'] - data_low['checkin']).days # Количество дней между заселением и выселением
    for i in mod_text['data']["body"]["searchResults"]["results"]:
        if count < number_of_hotels:
            name, street, dist, cost, id_hotel = info(i, callback)
            all_cost = int(''.join(re.findall(r"[\d+]", cost))) * int(all_days)
            text = f"Название отеля: {name}\nУлица: {street}\n" \
                   f"Расстояние до центра: {dist}\nСтоимость: {cost}\n" \
                   f"Общая стоимость {all_cost} {data_low['currency']}\n" \
                   f"Ссылка на отель: https://hotels.com/ho{id_hotel}"
            hotels.append(name)
            count += 1
            photo_list = find_photo(endpoint = 'properties/get-hotel-photos',
                                    hotel_id = id_hotel, photo_count = photo_count, callback = callback)
            media.append(types.InputMediaPhoto(media=photo_list[0], caption=text))
            for i_photo in photo_list[1:]:
                media.append(types.InputMediaPhoto(media=i_photo))
            bot.send_media_group(callback.from_user.id, media)
            media = []
            photo_list = []
    bot.send_message(callback.message.chat.id, "Запрос выполнен, выберете следующую команду\n"
                                               "/lowprice - список дешевых отелей\n/highprice - список дорогих отелей\n"
                                               "/bestdeal - список отелей по стоимости и расстоянию до цента\n"
                                               "/history - ответ на последний полученный запрос")
    insert_db(command, time, hotels)



def result_photo(choice_photo: str, mod_text: dict, callback: CallbackQuery) -> None:
    """
    Функция получает запрос о необходимости выводить фотографии, и в зависимости от этого
        выполняет определенную функцию
    Args:
        choice_photo: Ответ содержищий информацию о том, нужно ли выводить фото отеля или нет.
        mod_text: Словарь в котором содержится вся информация по городу, в котором необходимо реализовать
            поиск отелей.
        callback: Последний ответ от нашего телеграмм бота, по которому мы будем к нему обращаться
            для отправки сообщений.

    """
    if choice_photo == 'yes':
        result_yes(mod_text, callback)
    else:
        result_no(mod_text, callback)


@bot.message_handler(regexp=r"^Список дешевых отелей$")
@bot.message_handler(commands=['lowprice'])
@bot.message_handler(regexp=r"^Список дорогих отелей$")
@bot.message_handler(commands=['highprice'])
def lowprice_command(message: Message) -> None:  # Вводим команду lowprice
    """
    Функция получает определенные команды или текст, и в зависимости от команды мы должны будем найти
        самые дорогие или самые дешевые отели в определенном регионе.
    Args:
        message: Команда полученная от пользователя.

    """
    bot.set_state(message.from_user.id, UserInfoState.locale, message.chat.id)
    # bot.send_message(message.chat.id, f"Привет {message.from_user.first_name}"
    #                                   f", введи на каком языке вы хотите вводить город")  # Вводим город
    locale.locale_keyboard(message, sample_locales)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data_low:  # Да или Нет записываем в список
        if message.text == "Список дешевых отелей" or message.text == "/lowprice":
            data_low['command'] = "lowprice"
        if message.text == "Список дорогих отелей" or message.text == "/highprice":
            data_low['command'] = "highprice"
        data_low['time_command'] = datetime.utcfromtimestamp(int(message.date)).strftime('%Y-%m-%d %H:%M:%S')


@bot.callback_query_handler(func=None, state=UserInfoState.locale)
def lowprice_locale(callback: CallbackQuery) -> None: # Получаем язык
    """
    Функция получает от пользователя название страны, выбирает соответствующий язык и просит ввести валюту.
    Args:
        message: Название страны

    """
    bot.edit_message_text('Язык ввода успешно выбран', callback.message.chat.id, callback.message.id)
    with bot.retrieve_data(callback.from_user.id, callback.message.chat.id) as data_low:
        data_low['locale'] = callback.data # Записываем в список язык
    bot.set_state(callback.from_user.id, UserInfoState.currency, callback.message.chat.id)
    currency.currency_keyboard(callback, sample_currency)



@bot.callback_query_handler(func=None, state=UserInfoState.currency)
def lowprice_currency(callback: CallbackQuery) -> None: # Получаем валюту
    """
    Функция получает от пользователя название валюты, и просит ввести название города.
    Args:
        message: Название валюты

    """
    bot.edit_message_text('Валюта успешно выбрана', callback.message.chat.id, callback.message.id)
    with bot.retrieve_data(callback.from_user.id, callback.message.chat.id) as data_low:
        data_low['currency'] = callback.data # Записываем в список валюту
    bot.set_state(callback.from_user.id, UserInfoState.low_city, callback.message.chat.id)
    bot.send_message(callback.message.chat.id, 'Введите название города на выбранном языке')



@bot.message_handler(state=UserInfoState.low_city)
def lowprice_list_city(message: Message) -> None: # Получаем город
    """
    Функиция получает от пользователя название города и формирует обращение к API, чтобы
        уточнить регион по названию.
    Args:
        message: Название города, полученное от пользователя.

    """
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data_low:
        city_list = api_requests.location_processing(endpoint = api_requests.endpoint_search,
                                                     locale = data_low['locale'], currency = data_low['currency'],
                                                     city = message.text, user = message.from_user.id) # Формируем данные по городу
    try:
        mod_city = city_list['suggestions'][0]['entities'] #  Формируем запрос на получение необходимой информации
        if mod_city == []:
            bot.send_message(message.chat.id, 'Список городов пуст, вожмозно вы ввели название не на том языке, '
                                              'пожалуйста, повторите попытку')
            logger.info("ID пользователя - {user} | Полученный список городов пуст", user=message.from_user.id)
        else:
            city.city_keyboard(message, mod_city)
    except LookupError:
        bot.send_message(message.chat.id, 'Что-то пошло не так, введите город заново')
        logger.error("ID пользователя - {user} | Возникла ошибка при обращении к API", user=message.from_user.id)

@bot.callback_query_handler(func=None, state=UserInfoState.low_city)
def callback_city_id(callback: CallbackQuery) -> None:
    """
    Функция получает id города в качестве колбека, и отправляет пользователю следующее сообщение.
    Args:
        callback: ID города

    """
    bot.edit_message_text('Местоположение успешно выбрано', callback.message.chat.id, callback.message.id)
    with bot.retrieve_data(callback.from_user.id, callback.message.chat.id) as data_low:
        data_low['id_city'] = callback.data # Записываем в список id города
        if  data_low['command'] == "lowprice" or data_low['command'] == "highprice":
            bot.send_message(callback.message.chat.id, f'Сколько отелей необходимо вывести в результате?')  # Кол_во отелей
            bot.set_state(callback.from_user.id, UserInfoState.low_number_of_hotel, callback.message.chat.id)
        elif data_low['command'] == "bestdeal":
            bot.send_message(callback.message.chat.id, f'Введите минимальную цену для отеля')
            bot.set_state(callback.from_user.id, UserInfoState.low_price, callback.message.chat.id)


@bot.message_handler(state=UserInfoState.low_number_of_hotel)
def lowprice_get_num_hotel(message: Message) -> None:  # Вводим кол_во отелей
    """
    Функция получает количество отелей, проверяет необходимые условия, и если все верно выдает клавиатуру
    Args:
        message: Количество отелей, которые необходимо вывести в запросе, полученное от пользователя.

    """
    if not message.text.isdigit() or int(message.text) <= 0:
        bot.send_message(message.chat.id, 'Кол-во отелей является положительным числом')
        logger.info("ID пользователя - {user} | Введено недопустимое кол-во отелей", user=message.from_user.id)
    elif message.text.isdigit() and int(message.text) > 10:
        bot.send_message(message.chat.id, 'Кол-во отелей не может превышать 10')
        logger.info("ID пользователя - {user} | Введено кол-во отелей превышающее максимум", user=message.from_user.id)
    else:
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data_low:  # Берем кол-во отелей
            data_low['number_of_hotels'] = message.text
        text = f'Нужно ли загружать фотографии отелей?'
        yes_no.yes_no_keyboard(message, text) # Да или Нет


@bot.callback_query_handler(func=None, state=UserInfoState.low_number_of_hotel)
def callback_photo_choice(callback: CallbackQuery) -> None:
    """
    Функция получает ответ на то, нужно ли выводить фото или нет от пользователя, и в зависимоти от ответа,
        выполняет определенное действие
    Args:
        callback: "Да" или "Нет"

    """
    bot.delete_message(callback.message.chat.id, callback.message.id)
    with bot.retrieve_data(callback.from_user.id, callback.message.chat.id) as data_low:  # Фото, да или нет, в список
        data_low['choice_photo'] = callback.data
    if callback.data == 'yes':
        bot.set_state(callback.from_user.id, UserInfoState.photo_count, callback.message.chat.id)
        bot.send_message(callback.message.chat.id, 'Сколько фотографий хотите вывести?')
    elif callback.data == 'no':
        today = date.today()
        bot.set_state(callback.from_user.id, UserInfoState.checkin, callback.message.chat.id)
        calendar, step = DetailedTelegramCalendar(calendar_id=1, locale='ru', current_date=today, min_date=today,
                                                 max_date=today + timedelta(days=365)).build()
        bot.send_message(callback.message.chat.id, f"Select {LSTEP[step]}{calendar}", reply_markup=calendar)


@bot.message_handler(state=UserInfoState.photo_count)
def count_photo(message: Message) -> None:  # Вводим необходимое кол-во фотографий
    """
    Функция получает от пользователя необходимое для вывода в запросе количество фотографий, и проверяет условия
        и создает клавиатуру, в которой будет введена дата заселения в отель.
    Args:
        message: Количество фотографий, полученное от пользователя.

    """
    if message.text.isdigit() and int(message.text) <= 10:
        today = date.today()
        calendar, step = DetailedTelegramCalendar(calendar_id=1, locale='ru', current_date=today, min_date=today,
                                                 max_date=today + timedelta(days=365)).build()
        bot.send_message(message.chat.id, f"Select {LSTEP[step]}", reply_markup=calendar)
        bot.set_state(message.from_user.id, UserInfoState.checkin, message.chat.id)
    elif message.text.isdigit() and int(message.text) > 10:
        bot.send_message(message.chat.id, 'Кол-во фотографий не может превышать 10, введите число заново')
        logger.info("ID пользователя - {user} | Введено большое кол-во фото", user=message.from_user.id)
    else:
        bot.send_message(message.from_user.id, 'Кол-во фотографий является цифрой')
        logger.info("ID пользователя - {user} | Неверно введено кол-во фото", user=message.from_user.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data_low:  # Кол-во фото в список
        data_low['photo_count'] = message.text



@bot.callback_query_handler(func=None, state=UserInfoState.checkin) # Дата заселения
def call_date(callback: CallbackQuery) -> None:
    """
    Функция создает клаиватуру, в которой пользователю необходимо ввести дату, когда он хочет заселиться в отель,
        пользователь заполняет необходимую дату, и если все верно создается клавиатура для даты выселения из отеля
    Args:
        callback: Получает от пользователя в качестве колбека созданную клавиатуру.

    """
    all_steps = {'y': 'год', 'm': 'месяц', 'd': 'день'}
    today = date.today()
    result, key, step = DetailedTelegramCalendar(calendar_id=1, locale='ru', current_date=today, min_date=today,
                                                 max_date=today + timedelta(days=365)).process(callback.data)
    if not result and key:
        bot.edit_message_text(f"Выберите {all_steps[step]}", callback.message.chat.id,
                              callback.message.message_id, reply_markup=key)
    elif result:
        bot.edit_message_text(f"Дата заселения {result}\nТеперь выберите дату, когда бы вы хотели выселиться",
                              callback.message.chat.id, callback.message.message_id)
        bot.set_state(callback.from_user.id, UserInfoState.checkout, callback.message.chat.id)
        calendar, step = DetailedTelegramCalendar(calendar_id=2, locale='ru', current_date=today,
                                                  min_date=result + timedelta(days=1),
                                                  max_date=today + timedelta(days=365)).build()
        bot.send_message(callback.message.chat.id, f"Select {LSTEP[step]}", reply_markup=calendar)

    with bot.retrieve_data(callback.from_user.id, callback.message.chat.id) as data_low:  # Дата заселения
        data_low['checkin'] = result


@bot.callback_query_handler(func=None, state=UserInfoState.checkout)  # Дата заселения
def call_date_1(callback: CallbackQuery) -> None:
    """
    Функция получает от пользователя информацию, когда он хочет выселиться из отеля, и так как вся необходимая
        информация для запроса уже была получена, бот формирует полный ответ на запрос.
    Args:
        callback: Получает от пользователя в качестве колбека созданную клавиатуру.

    """
    all_steps = {'y':'год', 'm':'месяц', 'd':'день'}
    today = date.today()
    with bot.retrieve_data(callback.from_user.id, callback.message.chat.id) as data_low:  # Дата заселения
        day_in = data_low['checkin']
    result, key, step = DetailedTelegramCalendar(calendar_id=2, locale='ru', current_date=today,
                                                 min_date=day_in + timedelta(days=1),
                                                 max_date=today + timedelta(days=365)).process(callback.data)
    with bot.retrieve_data(callback.from_user.id, callback.message.chat.id) as data_low:  # Дата заселения
        checkin_date = data_low['checkin']
        data_low['checkout'] = result
    if not result and key:
        bot.edit_message_text(f"Выберите {all_steps[step]}", callback.message.chat.id,
                              callback.message.message_id, reply_markup=key)
    elif result:
        bot.edit_message_text(f"Дата выселение {result}\n", callback.message.chat.id, callback.message.message_id)
        bot.send_message(callback.message.chat.id, "Пожалуйста подождите, бот формирует ответ на ваш запрос")
        with bot.retrieve_data(callback.from_user.id, callback.message.chat.id) as data_low:
            if data_low['command'] != 'bestdeal':
                if data_low['command'] == "lowprice":
                    price = 'PRICE'
                elif data_low['command'] == "highprice":
                    price = 'PRICE_HIGHEST_FIRST'
                lowprice_text = api_requests.location_processing(
                    endpoint='properties/list', locale = data_low['locale'], currency = data_low['currency'],
                    city_id = data_low['id_city'], sort_order = price,
                    checkin = data_low['checkin'], checkout = data_low['checkout'], user = callback.from_user.id
                )
                result_photo(data_low['choice_photo'], lowprice_text, callback)
            else:
                price = 'STAR_RATING_HIGHEST_FIRST'
                best_hotels = []
                for i in range(1, 7):
                    bestdeal_text = api_requests.location_processing(
                        endpoint='properties/list', locale = data_low['locale'], currency = data_low['currency'],
                        city_id=data_low['id_city'], sort_order=price,
                        checkin=data_low['checkin'], checkout=data_low['checkout'],
                        price_min=data_low['low_price'], price_max=data_low['high_price'], number=i,
                        user = callback.from_user.id
                    )
                    best_hotels = result_bestdeal(data_low['choice_photo'], bestdeal_text, callback,
                                    data_low['low_dist'], data_low['high_dist'], best_hotels)
                best_result_photo(data_low['choice_photo'], best_hotels, callback)




