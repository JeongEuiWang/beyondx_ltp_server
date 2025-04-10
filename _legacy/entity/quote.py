from app.core.db import Base
from app.core.constants.enums import OrderStatusEnum, QuoteAddressTypeEnum
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Numeric, Boolean, Text, UniqueConstraint, Index, Enum
from datetime import datetime, UTC
from sqlalchemy.orm import relationship

class Quote(Base):
    __tablename__ = "quotes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    client_id = Column(Integer, ForeignKey("clients.id"))
    cargo_shipping_method_id = Column(Integer, ForeignKey("cargo_shipping_methods.id"))
    order_status = Column(Enum(OrderStatusEnum), nullable=False, default=OrderStatusEnum.ESTIMATE)
    region_id = Column(Integer, ForeignKey("service_regions.id"))
    order_primary_number = Column(String(100), nullable=False)
    order_additional_request = Column(Text)
    created_at = Column(DateTime, default=datetime.now(UTC))
    updated_at = Column(DateTime, onupdate=datetime.now(UTC))

    client = relationship("Client", back_populates="quotes")
    cargo_shipping_method = relationship("CargoShippingMethod", back_populates="quotes")
    cargo = relationship("QuoteCargo", back_populates="quote", uselist=False)
    locations = relationship("QuoteLocation", back_populates="quote")
    region = relationship("ServiceRegion", back_populates="quote")
    

    __table_args__ = (
        Index("idx_order_number", order_primary_number),
        Index("idx_status", order_status),
    )

class QuoteCargo(Base):
    __tablename__ = "quote_cargos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    quote_id = Column(Integer, ForeignKey("quotes.id"), unique=True)
    cargo_type_id = Column(Integer, ForeignKey("cargo_types.id"))
    cargo_width = Column(Numeric(15, 4), nullable=False)
    cargo_length = Column(Numeric(15, 4), nullable=False)
    cargo_height = Column(Numeric(15, 4), nullable=False)
    cargo_quantity = Column(Integer, nullable=False)
    cargo_weight = Column(Numeric(15, 4), nullable=False)
    cargo_stackable = Column(Boolean, nullable=False, default=False)
    cargo_stack_space = Column(Integer)
    is_hazardous = Column(Boolean, nullable=False, default=False)
    cargo_temperature = Column(String(20))

    quote = relationship("Quote", back_populates="cargo")
    cargo_type = relationship("CargoType", back_populates="cargo_details")

class QuoteLocation(Base):
    __tablename__ = "quote_locations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    quote_id = Column(Integer, ForeignKey("quotes.id"))
    type = Column(Enum(QuoteAddressTypeEnum), nullable=False)
    name = Column(String(100), nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    zipcode = Column(String(20), nullable=False)
    address = Column(Text, nullable=False)
    request_date = Column(DateTime)

    quote = relationship("Quote", back_populates="locations")

    __table_args__ = (
        UniqueConstraint("quote_id", "type", name="uq_quote_location_type"),
    )