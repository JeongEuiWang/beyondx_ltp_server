
from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.model._enum import LocationTypeEnum, OrderStatusEnum, ShipmentTypeEnum
from app.model._mixin import AutoIntegerIdMixin, TimestampMixin


class Quote(TimestampMixin, Base):
    __tablename__ = "quote"
    id = Column(String(32), primary_key=True)
    client_id = Column(Integer, ForeignKey("client.id"), nullable=False)
    cargo_transportation_id = Column(Integer, ForeignKey("cargo_transportation.id"), nullable=False)
    is_priority = Column(Boolean, nullable=False, default=False)

    total_weight = Column(Numeric(16, 4), nullable=False)
    total_price = Column(Numeric(16, 4), nullable=False)

    order_status = Column(Enum(OrderStatusEnum), nullable=False, default=OrderStatusEnum.ESTIMATE)
    order_primary = Column(String(255), nullable=False)
    order_additional_request = Column(Text)
    
    client = relationship("Client", back_populates="quote")
    cargo_transportation = relationship("CargoTransportation", back_populates="quote")
    quote_location = relationship("QuoteLocation", back_populates="quote")
    quote_cargo = relationship("QuoteCargo", back_populates="quote")

class QuoteLocation(AutoIntegerIdMixin, Base):
    __tablename__ = "quote_location"

    quote_id = Column(String(32), ForeignKey("quote.id"), nullable=False)
    state = Column(String(255), nullable=False)
    county = Column(String(255), nullable=False)
    city = Column(String(255), nullable=False)
    zip_code = Column(String(255), nullable=False)
    address = Column(String(255), nullable=False)
    location_type = Column(Enum(LocationTypeEnum), nullable=False)
    shipment_type = Column(Enum(ShipmentTypeEnum), nullable=False)
    request_datetime = Column(DateTime, nullable=False)
    
    quote = relationship("Quote", back_populates="quote_location")
    __table_args__ = (
        UniqueConstraint("quote_id", "shipment_type", name="uq_quote_location_shipment_type"),
    )

class QuoteLocationAccessorial(Base):
    __tablename__ = "quote_location_accessorial"

    quote_location_id = Column(Integer, ForeignKey("quote_location.id"), primary_key=True, nullable=False)
    cargo_accessorial_id = Column(Integer, ForeignKey("cargo_accessorial.id"), primary_key=True, nullable=False)

    quote_location = relationship("QuoteLocation", back_populates="quote_location_accessorial")
    cargo_accessorial = relationship("CargoAccessorial", back_populates="quote_location_accessorial")

    
class QuoteCargo(AutoIntegerIdMixin, Base):
    __tablename__ = "quote_cargo"

    quote_id = Column(String(32), ForeignKey("quote.id"), nullable=False)
    width = Column(Integer, nullable=False)
    length = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)
    package_description = Column(Text)
    cargo_stackable = Column(Boolean, nullable=False, default=False)
    cargo_temperature = Column(Text)
    is_hazardous = Column(Boolean, nullable=False, default=False)
    hazardous_detail = Column(Text)

    quote = relationship("Quote", back_populates="quote_cargo")
    
