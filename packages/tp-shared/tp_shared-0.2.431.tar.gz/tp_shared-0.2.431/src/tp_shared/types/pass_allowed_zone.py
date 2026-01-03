from enum import Enum, StrEnum


class PassAllowedZone(str, Enum):
    MKAD = "МКАД"
    SK = "СК"
    TTK = "ТТК"
    MO = "МО"


class PassAllowedZoneEn(StrEnum):
    MO = "MO"
    MKAD = "MKAD"
    TTK = "TTK"
    SK = "SK"
    NoZone = "NoZone"
