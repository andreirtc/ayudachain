from typing import Literal, Any
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class StrictModel(BaseModel):
    model_config=ConfigDict(extra='forbid')


class EvaluationMetadata(StrictModel):
    mode: Literal['local_synthetic_evaluation']
    identity_assurance: Literal['claimed_unverified']
    authentication: Literal['pending']
    impersonation_possible: Literal[True]
    blockchain_simulated: Literal[False]
    chain_time: Literal['actual']
    business_clock: Literal['wall_clock','simulated','mixed','unavailable','not_provisioned']
    simulated_services: list[str]
    digital_signatures: Literal['not_validated']
    real_data_ready: Literal[False]


class ActorView(StrictModel):
    id: UUID
    role: Literal['dswd','barangay','beneficiary','disbursing','auditor']
    display_name: str
    status: Literal['pending','active','deactivated']
    position: str | None
    barangay_id: UUID | None


class ContextView(StrictModel):
    actor_id: UUID
    run_id: UUID
    office_id: UUID
    role: Literal['dswd','barangay','beneficiary','disbursing','auditor']
    display_name: str
    barangay_id: UUID | None
    position: str | None
    household_id: UUID | None
    member_household_id: UUID | None
    identity_assurance: Literal['claimed_unverified']


class ReferenceView(StrictModel):
    id: UUID
    name: str


class ActorsResponse(StrictModel):
    data: list[ActorView]
    meta: EvaluationMetadata


class ContextResponse(StrictModel):
    data: ContextView
    meta: EvaluationMetadata


class ReferenceResponse(StrictModel):
    data: list[ReferenceView]
    meta: EvaluationMetadata
