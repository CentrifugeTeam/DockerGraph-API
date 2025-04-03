from typing import Annotated

from fastapi import Depends
from redis.asyncio import Redis
from sqlmodel.ext.asyncio.session import AsyncSession

from .conf import connection_pool, session_maker


async def get_session():
    async with session_maker() as session:
        yield session


async def get_redis():
    async with Redis(connection_pool=connection_pool) as r:
        yield r


Session = Annotated[AsyncSession, Depends(get_session)]
RedisSession = Annotated[Redis, Depends(get_redis)]
