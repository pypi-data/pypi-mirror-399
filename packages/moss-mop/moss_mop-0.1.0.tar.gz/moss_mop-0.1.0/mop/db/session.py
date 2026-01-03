from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from mop.conf import settings

engine = create_engine(
    settings.DATABASE_URI,
    echo=settings.DEBUG
)

SessionLocal = sessionmaker(
    engine,
    class_=Session,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

def get_session():
    with SessionLocal() as session:
        try:
            yield session
        finally:
            session.close()

SessionDep = Annotated[Session, Depends(get_session)]