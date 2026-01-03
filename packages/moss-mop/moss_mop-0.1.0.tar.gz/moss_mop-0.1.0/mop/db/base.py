from sqlalchemy.orm import declared_attr, declarative_base

from mop.conf import settings
from mop.util.strings import to_underline


class Base:
    @declared_attr
    def __tablename__(self):
        return f"{settings.DB_TABLE_PREFIX}{to_underline(self.__name__)}"

Base = declarative_base(cls=Base)