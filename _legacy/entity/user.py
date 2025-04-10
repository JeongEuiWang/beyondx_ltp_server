from app.core.db import Base
from app.core.constants.enums import RoleEnum
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum
from datetime import datetime, UTC
from sqlalchemy.orm import relationship

class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Enum(RoleEnum), nullable=False, default=RoleEnum.USER)

    users = relationship("User", back_populates="role")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.now(UTC))
    updated_at = Column(DateTime, onupdate=datetime.now(UTC))

    role = relationship("Role", back_populates="users")