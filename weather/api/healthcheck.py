import http

from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()


def is_disk_healthy():
    return True


def is_db_healthy():
    return True


@router.get("/health")
def healthcheck():
    disk = is_disk_healthy()
    db = is_db_healthy()

    if disk and db:
        status = http.HTTPStatus.OK
    else:
        status = http.HTTPStatus.INTERNAL_SERVER_ERROR

    return JSONResponse(
        status_code=200,
        content={
            "status": status,
            "disk": disk,
            "database": db,
        }
    )
