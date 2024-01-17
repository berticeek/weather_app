#!/usr/bin/env python3
import http
import json
from time import sleep

import pendulum
from loguru import logger
import uvicorn as uvicorn
from fastapi import FastAPI
import httpx
from fastapi_restful.tasks import repeat_every
from sqladmin import Admin, ModelView
from sqlmodel import create_engine, SQLModel, Session

from weather.api.measurements import router as measurements_router
from weather.models.measurement import Measurement, MeasurementAdmin
from weather.models.settings import Settings

app = FastAPI()
app.include_router(measurements_router)

settings = Settings()

# Create db schema
engine = create_engine(settings.db_uri)
SQLModel.metadata.create_all(engine)

# admin UI
admin = Admin(app, engine)
admin.add_view(MeasurementAdmin)


@app.get("/weather")
def get_weather():
    """Open json file with weather data and create model object"""

    logger.info("Getting weather")
    with open("weather_data.json", "r") as data_f:
        return json.load(data_f)


@app.on_event("startup")
@repeat_every(seconds=1200)
def retrieve_weather_data(q: str = "Kosice", units: str = 'metric', lang: str = "en"):
    """Cron job which periodically updates weather data and store them in the json file"""

    logger.info("Retrieving weather data.")
    params = {
        "q": q,
        "units": units,
        "appid": settings.api_token,
        "lang": lang
    }

    # Get weather data
    response = httpx.get(
        "https://api.openweathermap.org/data/2.5/weather", params=params, timeout=3)

    # Check status code and store data
    if response.status_code == http.HTTPStatus.OK:
        logger.info("Saving retrieved data")

        weather_data = response.json()

        measurement = Measurement(
            temperature=weather_data["main"]["temp"],
            humidity=weather_data["main"]["humidity"],
            pressure=weather_data["main"]["pressure"],
            city=weather_data["name"],
            country=weather_data["sys"]["country"],
            wind_speed=weather_data["wind"]["speed"],
            wind_direction=weather_data["wind"]["deg"],
            dt=pendulum.from_timestamp(weather_data["dt"]),
            sunrise=pendulum.from_timestamp(weather_data["sys"]["sunrise"]),
            sunset=pendulum.from_timestamp(weather_data["sys"]["sunset"]),
            icon=weather_data["weather"][0]["icon"]
        )

        with Session(engine) as session:
            session.add(measurement)
            session.commit()

        logger.info("Measurements successfully stored")
    else:
        logger.error(f"Data were not retrieved correctly. Status code: {response.status_code}")


def main():
    # run service
    uvicorn.run('weather.main:app', reload=True,
                host='127.0.0.1', port=8000)


if __name__ == '__main__':
    main()
