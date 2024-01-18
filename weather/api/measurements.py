import http

from fastapi_pagination.ext.sqlmodel import paginate
from fastapi_pagination.links import Page
from fastapi.responses import JSONResponse
from sqlalchemy.exc import NoResultFound
from sqlmodel import Session, select, desc
from fastapi import APIRouter, Depends

from weather.dependencies import get_session
from weather.models.ProblemDetails import ProblemDetails
from weather.models.measurement import Measurement

router = APIRouter()


@router.get("/api/measurements", response_model=Page[Measurement])
def list_measurements(session: Session = Depends(get_session)):
    """Get all weather measurement data for all cities, or select by city"""
    statement = select(Measurement)
    return paginate(session, statement)


@router.get("/api/measurements/last")
def get_last_measurement(session: Session = Depends(get_session)):
    """Get last weather entry"""
    statement = select(Measurement)
    return session.exec(statement.order_by(desc(Measurement.id))).first()


@router.get("/api/measurements/{slug}")
def get_measurement_by_slug(slug: int, session: Session = Depends(get_session)):
    """Get weather entry by its id"""
    statement = select(Measurement)

    result = session.exec(statement.where(Measurement.id == slug)).one_or_none()

    try:
        return session.exec(statement.where(Measurement.id == slug)).one()
    except NoResultFound as e:
        if result is None:
            content = ProblemDetails(
                status=http.HTTPStatus.NOT_FOUND,
                title="Measurement not found",
                detail=f"Measurement {slug} not found",
                instance=f"/api/measurements/{slug}"
            )

            return JSONResponse(
                status_code=content.status,
                content=content.model_dump(),
                media_type="application/problem+json"
            )
