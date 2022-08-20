from config_data import config
import requests

def search(city):
	url = "https://hotels4.p.rapidapi.com/locations/v2/search"

	querystring = {"query":city,"locale":'ru_RU',"currency":"USD"}

	headers = {
		"X-RapidAPI-Key": config.RAPID_API_KEY,
		"X-RapidAPI-Host": "hotels4.p.rapidapi.com"
	}

	response = requests.request("GET", url, headers=headers, params=querystring)

	return response.text