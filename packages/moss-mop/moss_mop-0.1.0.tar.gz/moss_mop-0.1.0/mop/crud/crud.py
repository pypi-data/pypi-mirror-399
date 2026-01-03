from typing import Generic, TypeVar

from sqlalchemy import select, func

from .page import ListSlice
from mop.db import AsyncSessionLocal, SessionLocal
from mop.entity import BaseEntity
from mop.error import DATA_NOT_FOUND, BizError

T = TypeVar("T", bound=BaseEntity)


class CrudBiz(Generic[T]):
    def __init__(self, model: type[T]):
        self.model = model

    def sync_find_all(self, **kwargs):
        filters = [self.model.deleted == False]

        for key, value in kwargs.items():
            if hasattr(self.model, key):
                filters.append(getattr(self.model, key) == value)

        with SessionLocal() as db:
            try:
                ret = db.execute(select(self.model).where(*filters))
                items = ret.scalars().all()
                return items
            finally:
                db.close()

    def sync_find_by_id(self, item_id: str):
        filters = [self.model.id == item_id, self.model.deleted == False]
        with SessionLocal() as db:
            try:
                ret = db.execute(select(self.model).where(*filters))
                ret = ret.scalars().first()
                if not ret:
                    raise BizError.init(DATA_NOT_FOUND)
                return ret
            finally:
                db.close()

    async def find_all(self, **kwargs):
        filters = [self.model.deleted == False]

        for key, value in kwargs.items():
            if hasattr(self.model, key):
                filters.append(getattr(self.model, key) == value)

        async with AsyncSessionLocal() as db:
            try:
                ret = await db.execute(select(self.model).where(*filters))
                items = ret.scalars().all()
                return items
            finally:
                await db.close()

    async def count_by(self, **kwargs):
        filters = [self.model.deleted == False]
        for key, value in kwargs.items():
            if hasattr(self.model, key):
                filters.append(getattr(self.model, key) == value)
        primary_column = self.model.__mapper__.primary_key[0]
        async with AsyncSessionLocal() as db:
            try:
                cnt = await db.execute(select(func.count(primary_column)).where(*filters))
                return cnt.scalar()
            finally:
                await db.close()

    async def _count_by(self, db: AsyncSessionLocal, *filters):
        primary_column = self.model.__mapper__.primary_key[0]
        cnt = await db.execute(select(func.count(primary_column)).where(*filters))
        return cnt.scalar()

    async def find_by(self, page_num: int = 1, page_size: int = 100, **kwargs):
        filters = [self.model.deleted == False]

        for key, value in kwargs.items():
            if hasattr(self.model, key):
                filters.append(getattr(self.model, key) == value)

        skip = (page_num - 1) * page_size
        async with AsyncSessionLocal() as db:
            try:
                print(filters)
                total = await self._count_by(db, *filters)
                ret = await db.execute(
                    select(self.model).where(*filters).offset(skip).limit(page_size)
                )
                items = ret.scalars().all()
                return ListSlice(
                    items=items, total=total, page_num=page_num, page_size=page_size
                )
            finally:
                await db.close()

    async def find_by_id(self, item_id: str):
        filters = [self.model.id == item_id, self.model.deleted == False]
        async with AsyncSessionLocal() as db:
            try:
                ret = await db.execute(select(self.model).where(*filters))
                ret = ret.scalars().first()
                if not ret:
                    raise BizError.init(DATA_NOT_FOUND)
                return ret
            finally:
                await db.close()

    async def find_one(self, **kwargs):
        filters = [self.model.deleted == False]

        for key, value in kwargs.items():
            if hasattr(self.model, key):
                filters.append(getattr(self.model, key) == value)

        async with AsyncSessionLocal() as db:
            try:
                ret = await db.execute(select(self.model).where(*filters))
                item = ret.scalars().first()
                return item
            finally:
                await db.close()

    async def create(self, **kwargs):
        item = self.model(**kwargs)
        item.default_created()
        async with AsyncSessionLocal() as db:
            try:
                db.add(item)
                await db.commit()
                await db.refresh(item)
                return item
            finally:
                await db.close()

    async def update(self, item_id: str, **kwargs):
        item = await self.find_by_id(item_id)

        other = self.model(**kwargs)
        item.update_attrs(other)

        async with AsyncSessionLocal() as db:
            try:
                db.add(item)
                await db.commit()
                await db.refresh(item)
                return item
            finally:
                await db.close()

    async def delete(self, item_id: str) -> bool:
        item = await self.find_by_id(item_id)
        item.default_deleted()
        async with AsyncSessionLocal() as db:
            try:
                db.add(item)
                await db.commit()
                await db.refresh(item)
                return True
            finally:
                await db.close()
        return False
