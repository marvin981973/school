import json

from app.tools.WebPageParsing import ScrapyPage
from time import time


class Weather:
    __weather_url = "http://www.nmc.cn/f/rest/real/"

    @staticmethod
    def get_weather_detail(city_code):
        res = json.loads(ScrapyPage(Weather.__weather_url + city_code + '?_=' + str(int(round(time() * 1000)))))
        return res

    @staticmethod
    def get_weather(city_code):
        res = Weather.get_weather_detail(city_code)
        return res["weather"]["info"]
