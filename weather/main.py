#!/usr/bin/env python3
import http
import json
from time import sleep

from loguru import logger

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
    logger.info("Getting weather")
    with open("weather_data.json", "r") as data_f:
        return json.load(data_f)


@app.on_event("startup")
@repeat_every(seconds=1200)
def retrieve_weather_data(q: str = "Kosice", units: str = 'metric', lang: str = "en"):
    logger.info("Retrieving weather data.")

    params = {
        "q": q,
        "units": units,
        "appid": "9e547051a2a00f2bf3e17a160063002d",
        "lang": lang
    }

    response = httpx.get(
        "https://api.openweathermap.org/data/2.5/weatherd", params=params)

    if response.status_code == http.HTTPStatus.OK:
        with open("weather_data.json", 'w') as data_f:
            json.dump(response.json(), data_f, indent=2)
    else:
        logger.error(f"Data were not retrieved correctly. Status code: {response.status_code}")


def main():
    uvicorn.run('weather.main:app', reload=True,
                host='127.0.0.1', port=8000)


if __name__ == '__main__':
    main()
