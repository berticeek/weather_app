#!/usr/bin/env python3
import json

from loguru import logger
import uvicorn as uvicorn
from fastapi import FastAPI
from sqladmin import Admin
from sqlmodel import create_engine, SQLModel

from weather.api.measurements import router as measurements_router
from weather.cron import router as cron_router
from weather.models.measurement import MeasurementAdmin
from weather.models.settings import Settings

app = FastAPI()
app.include_router(measurements_router)
app.include_router(cron_router)

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


def main():
    # run service
    uvicorn.run('weather.main:app', reload=True,
                host='127.0.0.1', port=8000)


if __name__ == '__main__':
    main()
