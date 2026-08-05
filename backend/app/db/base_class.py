from typing import Any
from sqlalchemy.orm import as_declarative, declared_attr
from sqlalchemy import Column, DateTime, Boolean
from datetime import datetime

@as_declarative()
class Base:
    id: Any
    __name__: str
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = Column(Boolean, default=False, index=True)

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
