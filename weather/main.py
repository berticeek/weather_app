#!/usr/bin/env python3
import json
from time import sleep

import uvicorn as uvicorn
from fastapi import FastAPI
import httpx
from fastapi_restful.tasks import repeat_every

app = FastAPI()


@app.get("/")
def hello():
    return "Hello, World!"


@app.get("/weather")
def get_weather():
    with open("weather_data.json", "r") as data_f:
        return json.load(data_f)


@app.on_event("startup")
@repeat_every(seconds=1200)
def retrieve_weather_data(q: str = "Kosice", units: str = 'metric', lang: str = "en"):
    print("retrieving weather data...")

    params = {
        "q": q,
        "units": units,
        "appid": "9e547051a2a00f2bf3e17a160063002d",
        "lang": lang
    }

    response = httpx.get(
        f"https://api.openweathermap.org/data/2.5/weather", params=params)

    with open("weather_data.json", 'w') as data_f:
        json.dump(response.json(), data_f, indent=2)

def main():
    uvicorn.run('weather.main:app', reload=True,
                host='127.0.0.1', port=8000)


if __name__ == '__main__':
    main()
