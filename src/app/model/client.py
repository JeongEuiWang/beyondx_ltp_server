
from sqlalchemy import Column, Enum, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.model._enum import ClientLevelEnum
from app.model._mixin import AutoIntegerIdMixin, TimestampMixin


class Client(AutoIntegerIdMixin, TimestampMixin, Base):
    __tablename__ = "client"

    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, unique=True)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    phone = Column(String(255), nullable=False)
    client_level_id = Column(Integer, ForeignKey("client_level.id"), nullable=False)
    total_payment_amount = Column(Numeric(16, 4), nullable=False, default=0)

    user = relationship("User", back_populates="client")
    client_level = relationship("ClientLevel", back_populates="client")
    client_address = relationship("ClientAddress", back_populates="client")

class ClientLevel(AutoIntegerIdMixin, Base):
    __tablename__ = "client_level"

    client_level = Column(Enum(ClientLevelEnum), nullable=False, default=ClientLevelEnum.DEFAULT)
    required_amount = Column(Numeric(16, 4), nullable=False, default=0)
    discount_rate = Column(Numeric(16, 4), nullable=False, default=0)

    client = relationship("Client", back_populates="client_level")
    

class ClientAddress(AutoIntegerIdMixin, TimestampMixin, Base):
    __tablename__ = "client_address"

    client_id = Column(Integer, ForeignKey("client.id"), nullable=False)
    name = Column(String(255), nullable=False) # 주소 별칭
    state = Column(String(255), nullable=False)
    county = Column(String(255), nullable=False)
    city = Column(String(255), nullable=False)
    zip_code = Column(String(255), nullable=False)
    address = Column(String(255))

    client = relationship("Client", back_populates="client_address")