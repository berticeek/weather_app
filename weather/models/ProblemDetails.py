from pydantic import BaseModel


class ProblemDetails(BaseModel):
    type: str = "about:blank"
    title: str
    status: int | None = None
    details: str | None = None
    instance: str | None = None
