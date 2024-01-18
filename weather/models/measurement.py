from datetime import datetime
from typing import Optional

from pydantic import BaseModel, HttpUrl, validator, field_validator
from sqladmin import ModelView
from sqlmodel import SQLModel, Field

from weather.dependencies import get_settings


class Measurement(SQLModel, table=True):
    """
    Data model for weather measurements
    Subclass of SQLModel, so we can store data in the database
    """

    id: int | None = Field(default=None, primary_key=True)
    temperature: float      # °C
    humidity: float
    pressure: float         # hPa
    city: str
    country: str
    wind_speed: float       # m/s
    wind_direction: int     # °
    dt: datetime            # UTC
    sunrise: datetime       # UTC
    sunset: datetime        # UTC
    icon: str


class MeasurementOut(BaseModel):
    city: str
    temperature: float
    url: HttpUrl = None

    @field_validator("url")
    @classmethod
    def set_url(cls, value, values):
        print(value)
        print(values)
        return f"{get_settings().base_url}/api/measurements/1"


class MeasurementAdmin(ModelView, model=Measurement):
    column_list = [
        Measurement.id,
        Measurement.dt,
        Measurement.temperature,
        Measurement.city,
        Measurement.sunrise,
        Measurement.sunset,
        Measurement.pressure,
        Measurement.humidity,
    ]
    icon = "fa-solid fa-temperature-quarter"
    page_size = 50
    column_searchable_list = [
        Measurement.city,
        Measurement.country,
    ]
    column_sortable_list = [
        Measurement.temperature,
        Measurement.sunrise,
        Measurement.sunset,
    ]