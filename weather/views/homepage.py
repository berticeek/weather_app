from pathlib import Path

import httpx
import pendulum
from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select, desc

from weather.api.measurements import get_last_measurement
from weather.dependencies import get_templates, get_settings, get_session
from weather.models.measurement import Measurement

router = APIRouter()


@router.get("/")
def homepage(request: Request,
             session: Session = Depends(get_session),
             templates: Jinja2Templates = Depends(get_templates)):

    statement = select(Measurement).order_by(desc(Measurement.id))
    weather = session.exec(statement).first()

    context = {
        "request": request,
        "message": "Hello world.",
        "now": pendulum.now(),
        "sunrise": pendulum.now(),
        "sunset": pendulum.now(),
        "weather": weather
    }

    return templates.TemplateResponse("current.weather.html", context=context)
