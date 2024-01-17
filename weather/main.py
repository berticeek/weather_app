#!/usr/bin/env python3
import json

from loguru import logger
import uvicorn as uvicorn
from fastapi import FastAPI
from sqladmin import Admin
from sqlmodel import create_engine, SQLModel

from weather.api.measurements import router as measurements_router
from weather.cron import router as cron_router
from weather.dependencies import get_settings
from weather.models.measurement import MeasurementAdmin
from weather.models.settings import Settings

app = FastAPI()

# Include routers, standard REST routers and cronjob
# Similar as they would be defined here in the main module, but for better organization they are
#  split into separated modules. By app.include_router they are included back here
app.include_router(measurements_router)
app.include_router(cron_router)

# Create db schema
engine = create_engine(get_settings().db_uri)
SQLModel.metadata.create_all(engine)

# admin UI
admin = Admin(app, engine)
admin.add_view(MeasurementAdmin)


def main():
    # run service
    uvicorn.run('weather.main:app', reload=True,
                host='127.0.0.1', port=8000)


if __name__ == '__main__':
    main()
