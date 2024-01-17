import http

import httpx
import pendulum
from fastapi import APIRouter
from fastapi_restful.tasks import repeat_every
from loguru import logger
from sqlalchemy import create_engine
from sqlmodel import Session

from weather.dependencies import get_settings
from weather.models.measurement import Measurement
from weather.models.settings import Settings

router = APIRouter()


@router.on_event("startup")
@repeat_every(seconds=1200)
def retrieve_weather_data(q: str = "Kosice", units: str = 'metric', lang: str = "en"):
    """Cron job which periodically updates weather data and store them in the json file"""

    logger.info("Retrieving weather data.")
    params = {
        "q": q,
        "units": units,
        "appid": get_settings().api_token,
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
        engine = create_engine(get_settings().db_uri)
        with Session(engine) as session:
            session.add(measurement)
            session.commit()

        logger.info("Measurements successfully stored")
    else:
        logger.error(f"Data were not retrieved correctly. Status code: {response.status_code}")