import requests
import json
import hendlers
from os import getenv
from dotenv import load_dotenv


class Weather:
    load_dotenv()
    url = 'https://api.openweathermap.org/data/2.5/weather'
    key = getenv('WEATHER_KEY')
    units = 'metric'

    def __init__(self, lat, lon, lang='ru'):
        self.lat = lat
        self.lon = lon
        self.lang = lang
        self.emoji = None
        self.location = None
        self.temp = None
        self.wind_speed = None
        self.wind_direction = None
        self.description = None
        self.humidity = None
        self.pressure = None

    async def get_weather(self):
        params = {
            'lat': self.lat,
            'lon': self.lon,
            'appid': Weather.key,
            'lang': self.lang,
            'units': Weather.units
        }
        response = requests.get(Weather.url, params=params)
        weather_dict = response.json()
        self.emoji = hendlers.get_emoji(weather_dict.get('weather')[0].get('id'))
        self.location = f'{weather_dict.get("name")}, {weather_dict.get("sys").get("country")}'
        self.temp = weather_dict.get('main').get('temp')
        self.wind_speed = weather_dict.get('wind').get('speed')
        self.wind_direction = hendlers.get_direction(int(weather_dict.get('wind').get('deg')))
        self.description = weather_dict.get('weather')[0].get('description').capitalize()
        self.humidity = weather_dict.get('main').get('humidity')
        self.pressure = int(weather_dict.get('main').get('pressure')) * 0.75
