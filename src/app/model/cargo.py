from sqlalchemy import Column, Integer, String
from app.db.base import Base
from app.model._mixin import AutoIntegerIdMixin


class CargoTransportation(AutoIntegerIdMixin, Base):
    __tablename__ = "cargo_transportation"

    name = Column(String(255), nullable=False)
    description = Column(String(255), nullable=False)


class CargoPackage(AutoIntegerIdMixin, Base):
    __tablename__ = "cargo_package"

    name = Column(String(255), nullable=False)
    width = Column(Integer, nullable=True)
    length = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)


class CargoAccessorial(AutoIntegerIdMixin, Base):
    __tablename__ = "cargo_accessorial"

    name = Column(String(255), nullable=False)
    description = Column(String(255), nullable=False)
