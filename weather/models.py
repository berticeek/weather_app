from pydantic import BaseModel
from datetime import datetime


class Measurement(BaseModel):
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
