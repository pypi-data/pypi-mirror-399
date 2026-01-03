from enum import StrEnum


class MosPassesGovernmentServiceType(StrEnum):
    YEAR_PASS = "YearPass"
    ONE_TIME_PASS = "OneTimePass"
    LARGE_AREA_PASS = "LargeAreaPass"
    ANNULATE_PASS = "AnnulPass"


class MosPassesOvgaTaskStatus(StrEnum):
    CREATED = "CREATED"
    IN_PROGRESS = "IN_PROGRESS"
    FAILED = "FAILED"
    CANCELED = "CANCELED"
    COMPLETED = "COMPLETED"
