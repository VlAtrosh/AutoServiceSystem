from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.models.client import Client
from typing import Optional, List


class ClientRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, client_id: str) -> Optional[Client]:
        result = await self.db.execute(select(Client).where(Client.id == client_id))
        return result.scalar_one_or_none()
    
    async def get_by_user_id(self, user_id: str) -> Optional[Client]:
        result = await self.db.execute(select(Client).where(Client.user_id == user_id))
        return result.scalar_one_or_none()
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Client]:
        result = await self.db.execute(select(Client).offset(skip).limit(limit))
        return result.scalars().all()
    
    async def get_by_status(self, status) -> List[Client]:
        result = await self.db.execute(select(Client).where(Client.status == status))
        return result.scalars().all()
    
    async def create(self, client: Client) -> Client:
        self.db.add(client)
        await self.db.commit()
        await self.db.refresh(client)
        return client
    
    async def update(self, client: Client) -> Client:
        await self.db.commit()
        await self.db.refresh(client)
        return client
    
    async def delete(self, client_id: str) -> bool:
        result = await self.db.execute(delete(Client).where(Client.id == client_id))
        await self.db.commit()
        return result.rowcount > 0