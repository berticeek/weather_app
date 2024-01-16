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
from sqlmodel import create_engine, SQLModel, Session, select, desc

from .models import Measurement, MeasurementAdmin

app = FastAPI()

# Create db schema
engine = create_engine("sqlite:///database.sqlite")
SQLModel.metadata.create_all(engine)

# admin UI
admin = Admin(app, engine)
admin.add_view(MeasurementAdmin)


def get_measurements_query(city):
    statement = select(Measurement)
    if city is not None:
        return statement.where(Measurement.city == city)
    return statement


@app.get("/get_all")
def get_all_measurements(city: str = None):
    """Get all weather measurement data for all cities, or select by city"""
    with Session(engine) as session:
        statement = get_measurements_query(city)
        return session.exec(statement).all()


@app.get("/get_last")
def get_last_measurement(city: str = None):
    with Session(engine) as session:
        statement = get_measurements_query(city)
        return session.exec(statement.order_by(desc(Measurement.id))).first()


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
        "appid": "9e547051a2a00f2bf3e17a160063002d",
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

        engine = create_engine("sqlite:///database.sqlite")
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
