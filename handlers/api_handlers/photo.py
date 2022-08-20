from config_data import config
import requests

def photo_find(id_hotel):
	url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"
	querystring = {"id": id_hotel}
	headers = {
		"X-RapidAPI-Key": config.RAPID_API_KEY,
		"X-RapidAPI-Host": "hotels4.p.rapidapi.com"
	}
	response = requests.request("GET", url, headers=headers, params=querystring)

	return response.text