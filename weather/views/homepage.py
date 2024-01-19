from pathlib import Path

import httpx
import pendulum
from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select, desc

from weather.api.measurements import get_last_measurement
from weather.dependencies import get_templates, get_settings, get_session
from weather.models.measurement import Measurement
from weather.models.settings import Settings

router = APIRouter()


@router.get("/")
def homepage(request: Request,
             settings: Settings = Depends(get_settings),
             session: Session = Depends(get_session),
             templates: Jinja2Templates = Depends(get_templates)):

    statement = select(Measurement).order_by(desc(Measurement.id))
    weather = session.exec(statement).first()

    context = {
        "request": request,
        "message": "Hello world.",
        "now": pendulum.now(),
        "sunrise": weather.sunrise,
        "sunset": weather.sunset,
        "weather": weather,
        "refresh": "45",
        "version": "2024.01",
        "environment": settings.environment,
        "background_nr": pendulum.now().hour // 2 + 1
    }

    return templates.TemplateResponse("current.weather.html", context=context)
