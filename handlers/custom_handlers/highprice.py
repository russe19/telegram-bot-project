from keyboards.reply.contact import request_contact
from loader import bot
from states.contact_information import UserInfoState
from telebot.types import Message
from handlers.api_handlers import search, json_text, hotel_highprice, photo
from telebot import types
import re
import json


"""
Функция lowprice_search используется ближе к концу кода, она нужна чтобы по городу найти id
Функции начинающиеся на result нужны чтобы найти необходимую информацию, когда бот уже получил все
необходимые данные, сначала идет result, а зетем в зависимости от ответа на вопрос про вывод фото "Да" или "Нет" 
выполняется соответствующая функция result_no или result_yes. Пока реализовал только так)
"""

def lowprice_search_high(city):  # функция для поиска id города
    search_city = search.search(city)  # через API Hotels ищем всю информацию по городу
    mod_search_city = str(json_text.json_mod(search_city, 'test.json'))  # Преобразовываем текст с помощью команд можуля json
    city_id = re.search(r"(?<='destinationId': ')\w+", mod_search_city)  # С помощью re ищем id города
    return city_id.group()

def result_no_high(mod, message):
    count = 0
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data_low:  # Берем кол-во отелей
        number_of_hotels = int(data_low['number_of_hotels'])
    for i in mod['data']["body"]["searchResults"]["results"]:
        if count < number_of_hotels:
            name, street, dist, cost, id_hotel = hotel_lowprice.info(i)
            bot.send_message(message.chat.id, f"Название отеля: {name}\nУлица: {street}\n"
                                              f"Расстояние до центра: {dist}\nСтоимость: {cost}")
            count += 1

def result_yes_high(mod, message):
    count = 0
    media = []
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data_low:  # Берем кол-во отелей
        number_of_hotels = int(data_low['number_of_hotels'])
        photo_count = int(data_low['photo_count'])
    for i in mod['data']["body"]["searchResults"]["results"]:
        if count < number_of_hotels:
            name, street, dist, cost, id_hotel = hotel_lowprice.info(i)
            text = f"Название отеля: {name}\nУлица: {street}\nРасстояние до центра: {dist}\nСтоимость: {cost}"
            count += 1
            photo_text = photo.photo_find(id_hotel)
            mod_photo = json_text.json_mod(photo_text, 'text3.json')
            mod_list = re.findall(r"(?<='baseUrl': ')\S+", str(mod_photo))
            photo_list = [i[:-2].format(size='z') for j, i in enumerate(mod_list) if j < photo_count]
            # with open('text3.json', 'w', encoding='utf-8') as file:
            #     json.dump(photo_list, file, ensure_ascii=False, indent=4)
            media.append(types.InputMediaPhoto(media=photo_list[0], caption=text))
            for i_photo in photo_list[1:]:
                media.append(types.InputMediaPhoto(media=i_photo))
            bot.send_media_group(message.from_user.id, media)
            media = []
            photo_list = []


def result_high(choice_photo, mod, message) -> None:
    if choice_photo == 'да':
        result_yes_high(mod, message)
    else:
        result_no_high(mod, message)


@bot.message_handler(commands=['highprice'])
def lowprice_command_high(message: Message) -> None:  # Вводим команду lowprice
    bot.set_state(message.from_user.id, UserInfoState.low_city, message.chat.id)
    bot.send_message(message.chat.id, f"Привет {message.from_user.first_name}, введи свой город")  # Вводим город


@bot.message_handler(state=UserInfoState.low_city)
def lowprice_get_city_high(message: Message) -> None:  # Вводим город
    if not message.text.isdigit():
        bot.send_message(message.from_user.id, 'Сколько отелей необходимо вывести в результате?')  # Кол_во отелей
        bot.set_state(message.from_user.id, UserInfoState.low_number_of_hotel, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data_low:  # Город записываем в список
            data_low['city'] = message.text

    else:
        bot.send_message(message.from_user.id, 'Название города не может сожержать цифры')


@bot.message_handler(state=UserInfoState.low_number_of_hotel)
def lowprice_get_num_hotel_high(message: Message) -> None:  # Вводим кол_во отелей
    if message.text.isdigit():
        bot.send_message(message.from_user.id, 'Нужно ли загружать фотографии отелей?')  # Да или Нет
        bot.set_state(message.from_user.id, UserInfoState.lowprice_choice_photo, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data_low:  # Да или Нет записываем в список
            data_low['number_of_hotels'] = message.text

    else:
        bot.send_message(message.from_user.id, 'Кол-во отелей может быть только числом')


@bot.message_handler(state=UserInfoState.lowprice_choice_photo)
def get_choice_photo_high(message: Message) -> None:  # Нужно ли загружать фотографии отелей?
    if message.text.lower() == 'да':
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data_low:
            data_low['id_city'] = lowprice_search(data_low['city'])  # Определен id города
            bot.set_state(message.from_user.id, UserInfoState.photo_count, message.chat.id)  # Кол-во фото
            bot.send_message(message.from_user.id, 'Сколько фотографий хотите вывести?')  # Кол-во фотографий
    elif message.text.lower() == 'нет':
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data_low:
            data_low['id_city'] = lowprice_search(data_low['city'])  # Определен id города
            bot.set_state(message.from_user.id, UserInfoState.checkin, message.chat.id)  # Состояние дата заселение
            bot.send_message(message.from_user.id,
                             'Введите в формате YYYY-MM-DD когда вы хотите заселиться')  # Когда заселение
    else:
        bot.send_message(message.from_user.id, 'Можно ответить только "Да" или "Нет"')
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data_low:  # Фото, да или нет, в список
        data_low['choice_photo'] = message.text


@bot.message_handler(state=UserInfoState.photo_count)
def count_photo_high(message: Message) -> None:  # Вводим необходимое кол-во фотографий
    if message.text.isdigit():
        bot.send_message(message.from_user.id, 'Введите в формате YYYY-MM-DD когда вы хотите заселиться')
        bot.set_state(message.from_user.id, UserInfoState.checkin, message.chat.id)
    else:
        bot.send_message(message.from_user.id, 'Кол-во фотографий является цифрой')
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data_low:  # Кол-во фото в список
        data_low['photo_count'] = message.text


@bot.message_handler(state=UserInfoState.checkin)
def date_checkin_high(message: Message) -> None:  # Вводим дату заселения
    if not message.text.isalpha():
        bot.send_message(message.from_user.id, 'Введите в формате YYYY-MM-DD когда вы хотите выселиться')
        bot.set_state(message.from_user.id, UserInfoState.checkout, message.chat.id)
    else:
        bot.send_message(message.from_user.id, 'Дата заселения не может содержать букв')
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data_low:  # Дата заселения
        data_low['checkin'] = message.text


@bot.message_handler(state=UserInfoState.checkout)
def date_checkout_high(message: Message) -> None:  # Вводим дату выселения
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data_low:  # Дата выселения
        data_low['checkout'] = message.text
        if not message.text.isalpha():
            lowprice_text = hotel_.search(data_low['id_city'], data_low['checkin'], data_low['checkout'])
            mod_lowprice = json_text.json_mod(lowprice_text, 'text2.json')
            result_high(data_low['choice_photo'], mod_lowprice, message)
        else:
            bot.send_message(message.from_user.id, 'Дата выселения не может содержать букв')