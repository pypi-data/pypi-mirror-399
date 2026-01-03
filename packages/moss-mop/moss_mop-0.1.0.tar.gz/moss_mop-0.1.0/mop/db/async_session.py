from typing import AsyncGenerator, Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from mop.conf import settings

async_engine = create_async_engine(
    settings.ASYNC_DATABASE_URI,
    echo=settings.DEBUG
)

AsyncSessionLocal = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    获取数据库会话依赖
    :return:
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

AsyncSessionDep = Annotated[AsyncSession, Depends(get_async_session)]
