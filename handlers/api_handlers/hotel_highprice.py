from config_data import config
import requests
import json
import re


def search(id, checkin, checkout):
    url = "https://hotels4.p.rapidapi.com/properties/list"

    querystring = {"destinationId":id,"pageNumber":"1","pageSize":"4","checkIn":checkin,"checkOut":checkout,"adults1":"1","sortOrder":"PRICE_HIGHEST_FIRST","locale":"ru_RU","currency":"USD"}

    headers = {
        "X-RapidAPI-Key": config.RAPID_API_KEY,
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)

    return response.text

def info(text):
    h_name = re.search(r"(?<='name': ')[^']+", str(text))
    h_street = re.search(r"(?<='streetAddress': ')[^']+", str(text))
    h_dist = re.search(r"(?<='distance': ')[^']+", str(text['landmarks']))
    h_cost = re.search(r"(?<='current': ')[^']+", str(text['ratePlan']))
    h_id = (re.search(r"(?<='id': )\w+", str(text)))
    return h_name.group(), h_street.group(), h_dist.group(), h_cost.group(), h_id.group()