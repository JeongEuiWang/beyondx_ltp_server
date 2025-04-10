from enum import StrEnum

class RoleEnum(StrEnum):
    ADMIN = "ADMIN"
    USER = "USER"

class ClientLevelEnum(StrEnum):
    DEFAULT = "DEFAULT"
    SILVER = "SILVER"
    GOLD = "GOLD"
    VIP = "VIP"

class QuoteAddressTypeEnum(StrEnum):
    PICKUP = "PICKUP"
    DELIVERY = "DELIVERY"

class OrderStatusEnum(StrEnum):
    ESTIMATE = "ESTIMATE"
    SUBMIT = "SUBMIT"
    ACCEPT = "ACCEPT"
    REJECT = "REJECT"
    COMPLETED = "COMPLETED"

class AreaTypeEnum(StrEnum):
  A = "A"
  B = "B"
  C = "C"

class TimezoneEnum(StrEnum):
  EST = "EST"
  MST = "MST"
  CST = "CST"
  PST = "PST"
