
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Integer


class TimestampMixin(object):
    created_at = Column(DateTime, default=datetime.now(UTC))
    updated_at = Column(DateTime, onupdate=datetime.now(UTC))

class AutoIntegerIdMixin(object):
    id = Column(Integer, primary_key=True, autoincrement=True)