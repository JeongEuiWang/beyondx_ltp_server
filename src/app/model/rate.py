from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.model._mixin import AutoIntegerIdMixin, TimestampMixin


# Local Rate의 기준이 되는 지역
class RateRegion(AutoIntegerIdMixin, TimestampMixin, Base):
    __tablename__ = "rate_region"

    name = Column(String(255), nullable=False)
    description = Column(String(255), nullable=False)

    rate_area = relationship("RateArea", back_populates="rate_region")
    rate_location = relationship("RateLocation", back_populates="rate_region")


# Region 기준으로 구분되는 Area의 종류
# 동일한 이름을 가지더라도 region_id에 따라 Unique로 설정된다.
class RateArea(AutoIntegerIdMixin, TimestampMixin, Base):
    __tablename__ = "rate_area"

    region_id = Column(Integer, ForeignKey("rate_region.id"), nullable=False)
    name = Column(String(255), nullable=False)
    min_load = Column(Numeric(16, 4), nullable=False)
    max_load = Column(Numeric(16, 4), nullable=False)
    max_load_weight = Column(Integer)

    rate_region = relationship("RateRegion", back_populates="rate_area")
    rate_area_cost = relationship("RateAreaCost", back_populates="rate_area")
    __table_args__ = (
        UniqueConstraint("region_id", "name", name="uq_region_area_name"),
    )

class RateAreaCost(AutoIntegerIdMixin, Base):
    __tablename__ = "rate_area_cost"

    area_id = Column(Integer, ForeignKey("rate_area.id"), nullable=False)
    min_weight = Column(Integer)
    max_weight = Column(Integer)
    price_per_weight = Column(Numeric(16, 4))

    rate_area = relationship("RateArea", back_populates="rate_area_cost")


class RateLocation(AutoIntegerIdMixin, TimestampMixin, Base):
    __tablename__ = "rate_location"

    area_id = Column(Integer, ForeignKey("rate_area.id"), nullable=False)
    region_id = Column(Integer, ForeignKey("rate_region.id"), nullable=False)
    state = Column(String(255), nullable=False)
    county = Column(String(255), nullable=False)
    city = Column(String(255), nullable=False)
    zip_code = Column(String(255), nullable=False)

    rate_region = relationship("RateRegion", back_populates="rate_location")

    __table_args__ = (
        UniqueConstraint("area_id", "zip_code", name="uq_rate_location"),
        Index("ix_rate_location_region_id", "region_id"),
        Index("ix_rate_location_region_area", "region_id", "area_id"),
    )
