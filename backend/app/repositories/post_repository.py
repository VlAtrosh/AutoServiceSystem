# app/repositories/post_repository.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from typing import List, Optional

from app.models.post import Post, PostStatus


class PostRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # ========== CREATE ==========
    async def create(self, post: Post) -> Post:
        """Добавить новый пост"""
        self.db.add(post)
        await self.db.commit()
        await self.db.refresh(post)
        return post
    
    # ========== READ ==========
    async def get_by_id(self, post_id: int) -> Optional[Post]:
        """Получить пост по ID"""
        result = await self.db.execute(
            select(Post).where(Post.id == post_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Post]:
        """Получить все посты с пагинацией"""
        result = await self.db.execute(
            select(Post).offset(skip).limit(limit)
        )
        return result.scalars().all()
    
    async def get_free_posts(self) -> List[Post]:
        """Получить все свободные посты"""
        result = await self.db.execute(
            select(Post).where(Post.status == PostStatus.FREE)
        )
        return result.scalars().all()
    
    async def get_busy_posts(self) -> List[Post]:
        """Получить все занятые посты"""
        result = await self.db.execute(
            select(Post).where(Post.status == PostStatus.BUSY)
        )
        return result.scalars().all()
    
    async def get_by_current_order(self, order_id: str) -> Optional[Post]:
        """Получить пост по текущему заказу"""
        result = await self.db.execute(
            select(Post).where(Post.current_order_id == order_id)
        )
        return result.scalar_one_or_none()
    
    # ========== UPDATE ==========
    async def update(self, post: Post) -> Post:
        """Обновить данные поста"""
        await self.db.commit()
        await self.db.refresh(post)
        return post
    
    async def occupy_post(self, post_id: int, order_id: str) -> Optional[Post]:
        """Занять пост заказом"""
        post = await self.get_by_id(post_id)
        if post and post.status == PostStatus.FREE:
            post.status = PostStatus.BUSY
            post.current_order_id = order_id
            await self.db.commit()
            await self.db.refresh(post)
        return post
    
    async def free_post(self, post_id: int) -> Optional[Post]:
        """Освободить пост"""
        post = await self.get_by_id(post_id)
        if post:
            post.status = PostStatus.FREE
            post.current_order_id = None
            await self.db.commit()
            await self.db.refresh(post)
        return post
    
    async def set_maintenance(self, post_id: int) -> Optional[Post]:
        """Перевести пост в обслуживание"""
        post = await self.get_by_id(post_id)
        if post:
            post.status = PostStatus.MAINTENANCE
            post.current_order_id = None
            await self.db.commit()
            await self.db.refresh(post)
        return post
    
    # ========== DELETE ==========
    async def delete(self, post_id: int) -> bool:
        """Удалить пост"""
        result = await self.db.execute(
            delete(Post).where(Post.id == post_id)
        )
        await self.db.commit()
        return result.rowcount > 0
    
    # ========== STATISTICS ==========
    async def count_by_status(self, status: PostStatus) -> int:
        """Количество постов по статусу"""
        result = await self.db.execute(
            select(func.count()).select_from(Post).where(Post.status == status)
        )
        return result.scalar() or 0
    
    async def count_free(self) -> int:
        """Количество свободных постов"""
        return await self.count_by_status(PostStatus.FREE)
    
    async def count_busy(self) -> int:
        """Количество занятых постов"""
        return await self.count_by_status(PostStatus.BUSY)
    
    async def count_all(self) -> int:
        """Общее количество постов"""
        result = await self.db.execute(
            select(func.count()).select_from(Post)
        )
        return result.scalar() or 0