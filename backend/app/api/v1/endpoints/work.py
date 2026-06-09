from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_admin, get_current_user, get_db
from app.models.user import User, UserRole
from app.models.work import Work
from app.schemas.work import WorkCreate, WorkUpdate, WorkResponse
from app.repositories.work_repository import WorkRepository
import uuid

router = APIRouter(prefix="/works", tags=["Справочник работ"])


@router.get("/", response_model=List[WorkResponse])
async def get_all_works(
    skip: int = 0,
    limit: int = 100,
    category: str = None,
    db: AsyncSession = Depends(get_db)
):
    """Получить список всех работ"""
    repo = WorkRepository(db)
    if category:
        return await repo.get_by_category(category, skip, limit)
    return await repo.get_all(skip, limit)


@router.get("/{work_id}", response_model=WorkResponse)
async def get_work(
    work_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Получить работу по ID"""
    repo = WorkRepository(db)
    work = await repo.get_by_id(work_id)
    if not work:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Work not found"
        )
    return work


@router.post("/", response_model=WorkResponse, status_code=status.HTTP_201_CREATED)
async def create_work(
    work_data: WorkCreate,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Создать новую работу (только админ)"""
    repo = WorkRepository(db)
    
    # Проверка на дубликат кода
    existing = await repo.get_by_code(work_data.code)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Work with this code already exists"
        )
    
    work = Work(
        id=str(uuid.uuid4()),
        code=work_data.code,
        name=work_data.name,
        description=work_data.description,
        price_per_hour=work_data.price_per_hour,
        min_hours=work_data.min_hours,
        max_hours=work_data.max_hours,
        category=work_data.category,
        subcategory=work_data.subcategory
    )
    return await repo.create(work)


@router.patch("/{work_id}", response_model=WorkResponse)
async def update_work(
    work_id: str,
    work_data: WorkUpdate,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Обновить работу (только админ)"""
    repo = WorkRepository(db)
    work = await repo.get_by_id(work_id)
    if not work:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Work not found"
        )
    
    update_data = work_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(work, field, value)
    
    return await repo.update(work)


@router.delete("/{work_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_work(
    work_id: str,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Удалить работу (только админ)"""
    repo = WorkRepository(db)
    deleted = await repo.delete(work_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Work not found"
        )