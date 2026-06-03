from fastapi import APIRouter

from .schemas import PartResponse, WorkResponse
from .service import ReferenceService

router = APIRouter(prefix="/api/v1/reference", tags=["reference"])


@router.get("/works", response_model=list[WorkResponse])
def get_works():
    works = ReferenceService.get_all_works()
    return [
        WorkResponse(id=w.id, name=w.name, price_per_hour=w.price_per_hour)
        for w in works
    ]


@router.get("/parts", response_model=list[PartResponse])
def get_parts():
    parts = ReferenceService.get_all_parts()
    return [
        PartResponse(id=p.id, name=p.name, article=p.article, price=p.price)
        for p in parts
    ]
