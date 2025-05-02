from sqlalchemy import Column, Enum, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.model._enum import LocationTypeEnum, UserLevelEnum, RoleEnum
from app.model._mixin import AutoIntegerIdMixin, TimestampMixin


class User(AutoIntegerIdMixin, TimestampMixin, Base):
    __tablename__ = "user"

    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey("role.id"), nullable=False)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    phone = Column(String(255), nullable=False)
    user_level_id = Column(Integer, ForeignKey("user_level.id"), nullable=False)
    total_payment_amount = Column(Numeric(16, 4), nullable=False, default=0)

    user_level = relationship("UserLevel", back_populates="user")
    user_address = relationship("UserAddress", back_populates="user")
    role = relationship("Role", back_populates="user")


class UserLevel(AutoIntegerIdMixin, Base):
    __tablename__ = "user_level"

    user_level = Column(
        Enum(UserLevelEnum), nullable=False, default=UserLevelEnum.DEFAULT
    )
    required_amount = Column(Numeric(16, 4), nullable=False, default=0)
    discount_rate = Column(Numeric(16, 4), nullable=False, default=0)

    user = relationship("User", back_populates="user_level")


class UserAddress(AutoIntegerIdMixin, TimestampMixin, Base):
    __tablename__ = "user_address"

    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    name = Column(String(255), nullable=False)  # 주소 별칭
    state = Column(String(255), nullable=False)
    county = Column(String(255), nullable=False)
    city = Column(String(255), nullable=False)
    zip_code = Column(String(255), nullable=False)
    location_type = Column(Enum(LocationTypeEnum), nullable=False)
    address = Column(String(255))

    user = relationship("User", back_populates="user_address")


class Role(AutoIntegerIdMixin, Base):
    __tablename__ = "role"

    role = Column(Enum(RoleEnum), nullable=False, default=RoleEnum.USER)
    user = relationship("User", back_populates="role")
