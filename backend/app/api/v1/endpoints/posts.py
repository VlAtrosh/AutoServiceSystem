from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_admin, get_db
from app.models.user import User
from app.schemas.post import PostResponse, PostCreate, PostOccupyRequest
from app.repositories.post_repository import PostRepository
from app.models.post import Post

router = APIRouter(prefix="/posts", tags=["Посты"])


@router.get("/", response_model=List[PostResponse])
async def get_all_posts(
    db: AsyncSession = Depends(get_db)
):
    """Получить список всех постов"""
    repo = PostRepository(db)
    return await repo.get_all()


@router.get("/free", response_model=List[PostResponse])
async def get_free_posts(
    db: AsyncSession = Depends(get_db)
):
    """Получить список свободных постов"""
    repo = PostRepository(db)
    return await repo.get_free_posts()


@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    post_data: PostCreate,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Создать новый пост (только админ)"""
    repo = PostRepository(db)
    post = Post(name=post_data.name)
    return await repo.create(post)


@router.post("/{post_id}/occupy", response_model=PostResponse)
async def occupy_post(
    post_id: int,
    request: PostOccupyRequest,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Занять пост заказом (только админ)"""
    repo = PostRepository(db)
    post = await repo.occupy(post_id, request.order_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found or already busy"
        )
    return post


@router.post("/{post_id}/free", response_model=PostResponse)
async def free_post(
    post_id: int,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Освободить пост (только админ)"""
    repo = PostRepository(db)
    post = await repo.free(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    return post


@router.post("/{post_id}/maintenance", response_model=PostResponse)
async def maintenance_post(
    post_id: int,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Перевести пост в обслуживание (только админ)"""
    repo = PostRepository(db)
    post = await repo.set_maintenance(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    return post