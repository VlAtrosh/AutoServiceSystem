from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.core.dependencies import get_current_admin, get_db
from app.models.user import User
from app.models.part import Part
from app.schemas.part import PartCreate, PartUpdate, PartResponse
from app.repositories.part_repository import PartRepository

router = APIRouter(prefix="/parts", tags=["Справочник запчастей"])


@router.get("/", response_model=List[PartResponse])
async def get_all_parts(
    skip: int = 0,
    limit: int = 100,
    category: str = None,
    brand: str = None,
    in_stock: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """Получить список всех запчастей"""
    repo = PartRepository(db)
    
    if in_stock:
        return await repo.get_in_stock(skip, limit)
    if category:
        return await repo.get_by_category(category, skip, limit)
    if brand:
        return await repo.get_by_brand(brand, skip, limit)
    
    return await repo.get_all(skip, limit)


@router.get("/low-stock", response_model=List[PartResponse])
async def get_low_stock_parts(
    threshold: int = 5,
    db: AsyncSession = Depends(get_db)
):
    """Получить запчасти с низким остатком"""
    repo = PartRepository(db)
    return await repo.get_low_stock(threshold)


@router.get("/out-of-stock", response_model=List[PartResponse])
async def get_out_of_stock_parts(
    db: AsyncSession = Depends(get_db)
):
    """Получить запчасти с нулевым остатком"""
    repo = PartRepository(db)
    return await repo.get_out_of_stock()


@router.get("/search", response_model=List[PartResponse])
async def search_parts(
    q: str,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Поиск запчастей"""
    repo = PartRepository(db)
    return await repo.search(q, skip, limit)


@router.get("/{part_id}", response_model=PartResponse)
async def get_part(
    part_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Получить запчасть по ID"""
    repo = PartRepository(db)
    part = await repo.get_by_id(part_id)
    if not part:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Part not found"
        )
    return part


@router.post("/", response_model=PartResponse, status_code=status.HTTP_201_CREATED)
async def create_part(
    part_data: PartCreate,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Создать новую запчасть (только админ)"""
    repo = PartRepository(db)
    
    # Проверка на дубликат кода
    existing = await repo.get_by_code(part_data.code)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Part with this code already exists"
        )
    
    # Проверка на дубликат артикула
    existing = await repo.get_by_article(part_data.article)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Part with this article already exists"
        )
    
    part = Part(
        id=str(uuid.uuid4()),
        code=part_data.code,
        article=part_data.article,
        name=part_data.name,
        description=part_data.description,
        price=part_data.price,
        purchase_price=part_data.purchase_price,
        quantity=part_data.quantity,
        warehouse=part_data.warehouse,
        category=part_data.category,
        brand=part_data.brand
    )
    return await repo.create(part)


@router.patch("/{part_id}", response_model=PartResponse)
async def update_part(
    part_id: str,
    part_data: PartUpdate,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Обновить запчасть (только админ)"""
    repo = PartRepository(db)
    part = await repo.get_by_id(part_id)
    if not part:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Part not found"
        )
    
    update_data = part_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(part, field, value)
    
    return await repo.update(part)


@router.delete("/{part_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_part(
    part_id: str,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Удалить запчасть (только админ)"""
    repo = PartRepository(db)
    deleted = await repo.delete(part_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Part not found"
        )