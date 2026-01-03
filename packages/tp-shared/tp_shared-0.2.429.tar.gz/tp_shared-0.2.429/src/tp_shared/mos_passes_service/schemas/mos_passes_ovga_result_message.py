from tp_helper.base_items.base_schema import BaseSchema

from tp_shared.mos_passes_service.types.mos_passes_service_types import (
    MosPassesGovernmentServiceType,
    MosPassesOvgaTaskStatus,
)
from tp_shared.types.pass_allowed_zone import PassAllowedZoneEn


class MosPassesOvgaResultStreamMessage(BaseSchema):
    carrier_id: int
    attorney_id: int

    # driver step
    driver_ovga_id: int | None = None
    driver_step_done_at: int | None = None

    # vehicle step
    vehicle_ovga_id: int | None = None
    vehicle_step_done_at: int | None = None

    # contract step
    contract_ovga_id: int | None = None
    contract_step_done_at: int | None = None

    # pass request step
    pass_ovga_id: int | None = None
    pass_step_done_at: int | None = None

    status: MosPassesOvgaTaskStatus
    error_message: str | None = None
    completed_at: int | None = None
    canceled_at: int | None = None
    zone: PassAllowedZoneEn
    service_type: MosPassesGovernmentServiceType

    created_at: int
    updated_at: int
