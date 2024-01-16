#!/usr/bin/env python3
import http
import json
from time import sleep

from loguru import logger
import uvicorn as uvicorn
from fastapi import FastAPI
import httpx
from fastapi_restful.tasks import repeat_every
from sqlmodel import create_engine, SQLModel

from .models import Measurement

app = FastAPI()


@app.get("/")
def hello():
    """Index page"""

    return "Hello, World!"


@app.get("/weather")
def get_weather():
    """Open json file with weather data and create model object"""

    logger.info("Getting weather")
    with open("weather_data.json", "r") as data_f:
        weather_data = json.load(data_f)

    measurement = Measurement(
        temperature=weather_data["main"]["temp"],
        humidity=weather_data["main"]["humidity"],
        pressure=weather_data["main"]["pressure"],
        city=weather_data["name"],
        country=weather_data["sys"]["country"],
        wind_speed=weather_data["wind"]["speed"],
        wind_direction=weather_data["wind"]["deg"],
        dt=weather_data["dt"],
        sunrise=weather_data["sys"]["sunrise"],
        sunset=weather_data["sys"]["sunset"],
        icon=weather_data["weather"][0]["icon"]
    )


@app.on_event("startup")
@repeat_every(seconds=1200)
def retrieve_weather_data(q: str = "Kosice", units: str = 'metric', lang: str = "en"):
    """Cron job which periodically updates weather data and store them in the json file"""

    logger.info("Retrieving weather data.")
    params = {
        "q": q,
        "units": units,
        "appid": "9e547051a2a00f2bf3e17a160063002d",
        "lang": lang
    }

    # Get weather data
    response = httpx.get(
        "https://api.openweathermap.org/data/2.5/weather", params=params, timeout=3)

    # Check status code and store data
    if response.status_code == http.HTTPStatus.OK:
        logger.info("Saving retrieved data")

        with open("weather_data.json", 'w') as data_f:
            json.dump(response.json(), data_f, indent=2)
    else:
        logger.error(f"Data were not retrieved correctly. Status code: {response.status_code}")


def main():
    # Create db schema
    engine = create_engine("sqlite:///database.sql")
    SQLModel.metadata.create_all(engine)

    # run service
    uvicorn.run('weather.main:app', reload=True,
                host='127.0.0.1', port=8000)


if __name__ == '__main__':
    main()
