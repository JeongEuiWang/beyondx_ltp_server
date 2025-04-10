from app.core.db import Base
from app.core.constants.enums import AreaTypeEnum, TimezoneEnum
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Numeric, Text, Boolean, UniqueConstraint, Enum
from sqlalchemy.orm import relationship


class ServiceAreaType(Base):
  __tablename__ = "service_area_types"

  id = Column(Integer, primary_key=True, autoincrement=True)
  area_type = Column(Enum(AreaTypeEnum), nullable=False)

  area_codes = relationship("ServiceAreaCode", back_populates="area_type")

class ServiceTimezone(Base):
  __tablename__ = "service_timezones"

  id = Column(Integer, primary_key=True, autoincrement=True)
  timezone = Column(Enum(TimezoneEnum), nullable=False)

  regions = relationship("ServiceRegion", back_populates="timezone")

class ServiceRegion(Base):
  __tablename__ = "service_regions"

  id = Column(Integer, primary_key=True, autoincrement=True)
  region_name = Column(String(100), nullable=False)
  is_active = Column(Boolean, nullable=False, default=True)
  timezone_id = Column(Integer, ForeignKey("service_timezones.id"))
  description = Column(Text)

  timezone = relationship("ServiceTimezone", back_populates="regions")
  area_codes = relationship("ServiceAreaCode", back_populates="region")

class ServiceAreaCode(Base):
  __tablename__ = "service_area_codes"

  id = Column(Integer, primary_key=True, autoincrement=True)
  city = Column(String(100), nullable=False)
  zipcode = Column(String(20), nullable=False)
  state = Column(String(100), nullable=False)
  area_type_id = Column(Integer, ForeignKey("service_area_types.id"))
  region_id = Column(Integer, ForeignKey("service_regions.id"))

  area_type = relationship("ServiceAreaType", back_populates="area_codes")
  region = relationship("ServiceRegion", back_populates="area_codes")

  __table_args__ = (
      UniqueConstraint("city", "state", "zipcode", name="uq_area_location"),
  )