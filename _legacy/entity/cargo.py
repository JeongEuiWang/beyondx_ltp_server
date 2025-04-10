from app.core.db import Base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Numeric, Boolean
from sqlalchemy.orm import relationship

class CargoShippingMethod(Base):
    __tablename__ = "cargo_shipping_methods"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)

    quotes = relationship("Quote", back_populates="cargo_shipping_methods")

class CargoType(Base):
    __tablename__ = "cargo_types"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(250), nullable=False)
    length = Column(Numeric(15, 4))
    width = Column(Numeric(15, 4))
    height = Column(Numeric(15, 4))

    cargo_details = relationship("QuoteCargo", back_populates="cargo_type")