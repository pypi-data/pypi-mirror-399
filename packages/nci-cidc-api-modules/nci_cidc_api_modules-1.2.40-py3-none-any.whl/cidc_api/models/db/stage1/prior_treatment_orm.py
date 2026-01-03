from __future__ import annotations
from typing import List

from pydantic import NonPositiveInt, NegativeInt
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from cidc_api.models.db.stage1.base_orm import BaseORM
from cidc_api.models.types import PriorTreatmentType, ConditioningRegimenType, StemCellDonorType


class PriorTreatmentORM(BaseORM):
    __tablename__ = "prior_treatment"
    __repr_attrs__ = ["prior_treatment_id", "type"]
    __table_args__ = {"schema": "stage1"}
    __data_category__ = "prior_treatment"

    prior_treatment_id: Mapped[int] = mapped_column(primary_key=True)
    participant_id: Mapped[int] = mapped_column(ForeignKey("stage1.participant.participant_id", ondelete="CASCADE"))

    prior_treatment_days_to_start: Mapped[NonPositiveInt | None]
    prior_treatment_days_to_end: Mapped[NonPositiveInt | None]
    prior_treatment_type: Mapped[List[PriorTreatmentType]] = mapped_column(JSON, nullable=False)
    prior_treatment_description: Mapped[str | None]
    prior_treatment_best_response: Mapped[str | None]
    prior_treatment_conditioning_regimen_type: Mapped[ConditioningRegimenType | None]
    prior_treatment_stem_cell_donor_type: Mapped[StemCellDonorType | None]
    prior_treatment_days_to_prior_transplant: Mapped[NegativeInt | None]

    participant: Mapped[ParticipantORM] = relationship(back_populates="prior_treatments", cascade="all, delete")
