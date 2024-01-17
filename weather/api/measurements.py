from sqlmodel import create_engine, Session, select, desc
from fastapi import APIRouter

from weather.models.measurement import Measurement
from weather.models.settings import Settings

settings = Settings()
router = APIRouter()


@router.get("/api/measurements")
def list_measurements(city: str = None):
    """Get all weather measurement data for all cities, or select by city"""

    engine = create_engine(settings.db_uri)

    with Session(engine) as session:
        statement = select(Measurement)
        if city is not None:
            statement = statement.where(Measurement.city == city)
        return session.exec(statement).all()


@router.get("/api/measurements/last")
def get_last_measurement(city: str = None):
    """Get last weather entry"""

    engine = create_engine(settings.db_uri)

    with Session(engine) as session:
        statement = select(Measurement)
        if city is not None:
            statement = statement.where(Measurement.city == city)
        return session.exec(statement.order_by(desc(Measurement.id))).first()