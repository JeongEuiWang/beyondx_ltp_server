from enum import StrEnum

class RoleEnum(StrEnum):
    USER = "USER"
    ADMIN = "ADMIN"

class ClientLevelEnum(StrEnum):
    DEFAULT = "DEFAULT"
    SILVER = "SILVER"
    GOLD = "GOLD"
    VIP = "VIP"

class ShippingTypeEnum(StrEnum):
    PICKUP = "PICKUP"
    DELIVERY = "DELIVERY"


class OrderStatusEnum(StrEnum):
    ESTIMATE = "ESTIMATE"
    SUBMIT = "SUBMIT"
    ACCEPT = "ACCEPT"
    REJECT = "REJECT"
    COMPLETED = "COMPLETED"

class ShipmentTypeEnum(StrEnum):
    PICKUP = "PICKUP"
    DELIVERY = "DELIVERY"

class LocationTypeEnum(StrEnum):
    COMMERCIAL = "COMMERCIAL"
    RESIDENTIAL = "RESIDENTIAL"
    AIRPORT = "AIRPORT"
