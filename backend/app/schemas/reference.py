from pydantic import BaseModel


class WorkResponse(BaseModel):
    id: str
    name: str
    price_per_hour: float


class PartResponse(BaseModel):
    id: str
    name: str
    article: str
    price: float
