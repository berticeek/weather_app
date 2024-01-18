from pathlib import Path

from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates

from weather.dependencies import get_templates

router = APIRouter()


@router.get("/")
def homepage(request: Request, templates: Jinja2Templates = Depends(get_templates)):
    context = {
        "request": request,
        "message": "Hello world."
    }

    return templates.TemplateResponse("hello.html", context=context)
