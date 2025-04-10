from app.core.db import Base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Numeric, Text, Enum
from datetime import datetime, UTC
from sqlalchemy.orm import relationship
from app.core.constants.enums import ClientLevelEnum


class Client(Base):
    __tablename__ = "clients"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    first_name = Column(String(250), nullable=False)
    last_name = Column(String(250), nullable=False)
    phone = Column(String(100), nullable=False)
    client_level_id = Column(Integer, ForeignKey("client_levels.id"), default=ClientLevelEnum.DEFAULT)
    total_payment_amount = Column(Numeric(15, 4), nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.now(UTC))
    updated_at = Column(DateTime, onupdate=datetime.now(UTC))

    user = relationship("User", back_populates="client")
    client_level = relationship("ClientLevel", back_populates="clients")
    addresses = relationship("ClientAddress", back_populates="client")
    quotes = relationship("Quote", back_populates="client")

class ClientLevel(Base):
    __tablename__ = "client_levels"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Enum(ClientLevelEnum), nullable=False, default=ClientLevelEnum.DEFAULT)
    required_amount = Column(Numeric(15, 4), nullable=False)
    discount_rate = Column(Numeric(3, 2), nullable=False)
    clients = relationship("Client", back_populates="client_level")

class ClientAddress(Base):
    __tablename__ = "client_addresses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    client_id = Column(Integer, ForeignKey("clients.id"))
    name = Column(String(100), nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    zipcode = Column(String(20), nullable=False)
    address = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now(UTC))
    updated_at = Column(DateTime, onupdate=datetime.now(UTC))

    client = relationship("Client", back_populates="addresses")
