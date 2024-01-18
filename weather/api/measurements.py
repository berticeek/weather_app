import http

from fastapi_pagination.ext.sqlmodel import paginate
from fastapi_pagination.links import Page
from sqlalchemy.exc import NoResultFound
from sqlmodel import Session, select, desc
from fastapi import APIRouter, Depends

from weather.dependencies import get_session
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
    try:
        return session.exec(statement.where(Measurement.id == slug)).one()
    except NoResultFound as e:
        return {"error": f"Measurement with id {slug} doesn't exist"}
