from pydantic import BaseModel


class CarCreate(BaseModel):
    brand: str
    model: str
    year: int
    license_plate: str
    vin: str
    color: str


class CarUpdate(BaseModel):
    brand: str | None = None
    model: str | None = None
    year: int | None = None
    license_plate: str | None = None
    vin: str | None = None
    color: str | None = None


class CarResponse(BaseModel):
    id: str
    client_id: str
    brand: str
    model: str
    year: int
    license_plate: str
    vin: str
    color: str
