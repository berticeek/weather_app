from sqlmodel import create_engine, Session, select, desc
from fastapi import APIRouter, Depends

from weather.dependencies import get_settings, get_session
from weather.models.measurement import Measurement
from weather.models.pager import Pager
from weather.models.settings import Settings

router = APIRouter()


@router.get("/api/measurements")
def list_measurements(page: int = 1,
                      page_size: int = 20,
                      session: Session = Depends(get_session)):
    """Get all weather measurement data for all cities, or select by city"""

    # Pagination, offset is from which index to start and limit is how many rows to select
    statement = (
        select(Measurement)
        .offset((page-1) * page_size)
        .limit(page_size)
    )
    results = session.exec(statement).all()

    return Pager(
        first=f"http://localhost:8000/api/measurements?page=1&page_size={page_size}",
        results=list(results),
        count=len(results)
    )


@router.get("/api/measurements/last")
def get_last_measurement(session: Session = Depends(get_session)):
    """Get last weather entry"""
    statement = select(Measurement)
    return session.exec(statement.order_by(desc(Measurement.id))).first()
