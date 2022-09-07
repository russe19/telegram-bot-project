from config_data import config
import requests
import json
import re
from loguru import logger

endpoint_search = 'locations/v2/search'
endpoint_hotels = 'properties/list'
endpoint_photo = 'properties/get-hotel-photos'

logger.add("debug/debug.log", format="{time} | {level} | ID пользователя - {message}", level="INFO",
           rotation="100 MB", compression="zip")

def json_mod(text, file_name):
    data = json.loads(text)

    with open(file_name, 'w', encoding='utf-8') as file:
        mod = json.dump(data, file, ensure_ascii=False, indent=4)

    with open(file_name, 'r', encoding='utf-8') as file:
        mod_text = json.load(file)

    return mod_text



def location_processing(endpoint, locale=None, currency=None, city=None, city_id=None, checkin=None, checkout=None, sort_order=None,
                        hotel_id=None, price_min=None, price_max=None,
                        number=None, user=None):  # функция для поиска id города
    search_city = api_requests(endpoint, locale, currency, city, city_id, checkin,
                               checkout, sort_order, hotel_id, price_min, price_max,
                               number, user)  # через API Hotels ищем всю информацию по городу
    mod_search_city = json.loads(search_city)  # Преобразовываем текст с помощью команд можуля json
    return mod_search_city


def api_requests(endpoint, locale=None, currency=None, city=None, city_id=None, checkin=None, checkout=None, sort_order=None,
                 hotel_id=None, price_min=None, price_max=None, number=None, user=None):
    url = f"https://hotels4.p.rapidapi.com/{endpoint}"
    querystring = {}

    if endpoint == 'locations/v2/search':
        querystring = {"query": city, "locale": locale, "currency": currency}
    elif endpoint == 'properties/list' and sort_order == 'STAR_RATING_HIGHEST_FIRST':
        querystring = {"destinationId": city_id, "pageNumber": f"{number}", "pageSize": "25", "checkIn": checkin,
                       "checkOut": checkout, "adults1": "1", "priceMin": price_min, "priceMax": price_max,
                       "sortOrder": sort_order, "locale": locale, "currency": currency, "landmarkIds": "Центр города"}
    elif endpoint == 'properties/list':
        querystring = {"destinationId": city_id, "pageNumber": "1", "pageSize": "25", "checkIn": checkin,
                       "checkOut": checkout, "adults1": "1", "sortOrder": sort_order, "locale": locale,
                       "currency": currency}
    elif endpoint == 'properties/get-hotel-photos':
        querystring = {"id": hotel_id}

    headers = {
        "X-RapidAPI-Key": config.RAPID_API_KEY,
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }

    try:
        response = requests.request("GET", url, headers=headers, params=querystring, timeout=30)
        return response.text
    except requests.exceptions.RequestException as exc:
        logger.info(user)
        return False



# t = location_processing(city='Нью-Йорк', endpoint=endpoint_search)
