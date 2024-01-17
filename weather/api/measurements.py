from sqlmodel import create_engine, Session, select, desc
from fastapi import APIRouter, Depends

from weather.dependencies import get_settings, get_session
from weather.models.measurement import Measurement
from weather.models.settings import Settings

router = APIRouter()


@router.get("/api/measurements")
def list_measurements(session: Session = Depends(get_session)):
    """Get all weather measurement data for all cities, or select by city"""
    statement = select(Measurement)
    return session.exec(statement).all()


@router.get("/api/measurements/last")
def get_last_measurement(session: Session = Depends(get_session)):
    """Get last weather entry"""
    statement = select(Measurement)
    return session.exec(statement.order_by(desc(Measurement.id))).first()