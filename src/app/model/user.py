
from sqlalchemy import Column, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.model._mixin import AutoIntegerIdMixin, TimestampMixin
from app.model._enum import RoleEnum

class User(AutoIntegerIdMixin, TimestampMixin, Base):
    __tablename__ = "user"

    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey("role.id"), nullable=False)
    role = relationship("Role", back_populates="user")
    client = relationship("Client", back_populates="user")

class Role(AutoIntegerIdMixin, Base):
    __tablename__ = "role"

    role = Column(Enum(RoleEnum), nullable=False, default=RoleEnum.USER)
    user = relationship("User", back_populates="role")