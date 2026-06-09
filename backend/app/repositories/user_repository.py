from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.schemas.auth import UserCreate
import uuid


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, user_id: str) -> User | None:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    
    async def get_by_username(self, username: str) -> User | None:
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    
    async def create_user(self, user_data: UserCreate, hashed_password: str) -> User:
        user = User(
            id=str(uuid.uuid4()),
            username=user_data.username,
            email=user_data.email,
            last_name=user_data.last_name,
            first_name=user_data.first_name,
            middle_name=user_data.middle_name if hasattr(user_data, 'middle_name') else None,
            phone=user_data.phone,
            hashed_password=hashed_password,
            role=user_data.role
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def update_user(self, user: User) -> User:
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def delete_user(self, user_id: str) -> bool:
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user:
            await self.db.delete(user)
            await self.db.commit()
            return True
        return False
    
    async def exists_by_username(self, username: str) -> bool:
        result = await self.db.execute(select(User.id).where(User.username == username))
        return result.scalar_one_or_none() is not None
    
    async def exists_by_email(self, email: str) -> bool:
        result = await self.db.execute(select(User.id).where(User.email == email))
        return result.scalar_one_or_none() is not None