from datetime import datetime

from sqlalchemy import Column, String, Boolean, DateTime, text, Integer

from mop.db import Base
from mop.snowflake import IDWorker


class BaseEntity(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(32), nullable=False)
    deleted = Column(Boolean, nullable=False, server_default=text("false"))
    created_by = Column(String(32), nullable=True)
    created_at = Column(DateTime, nullable=True, default=datetime.now)
    updated_by = Column(String(32), nullable=True)
    updated_at = Column(DateTime, nullable=True, default=datetime.now)
    deleted_by = Column(String(32), nullable=True)
    deleted_at = Column(DateTime, nullable=True)

    def default_created(self):
        self.id = IDWorker.gen_id()
        self.tenant_id = '000000'

    def update_attrs(self, other):
        for attr in other.__dict__.keys():
            if hasattr(self, attr) and attr != 'id' and attr != '_sa_instance_state':
                setattr(self, attr, getattr(other, attr))
        self.updated_at = datetime.now()

    def default_deleted(self):
        self.deleted = True
        self.deleted_at = datetime.now()



