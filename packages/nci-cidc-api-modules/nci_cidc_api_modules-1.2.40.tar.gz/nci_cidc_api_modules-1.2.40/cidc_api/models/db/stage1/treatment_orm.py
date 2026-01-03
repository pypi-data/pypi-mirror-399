from __future__ import annotations
from typing import List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cidc_api.models.db.stage1.base_orm import BaseORM
from cidc_api.models.types import YNU, OffTreatmentReason


class TreatmentORM(BaseORM):
    __tablename__ = "treatment"
    __repr_attrs__ = ["treatment_id", "participant_id", "treatment_description"]
    __table_args__ = {"schema": "stage1"}
    __data_category__ = "treatment"

    treatment_id: Mapped[int] = mapped_column(primary_key=True)
    participant_id: Mapped[int] = mapped_column(ForeignKey("stage1.participant.participant_id", ondelete="CASCADE"))
    arm: Mapped[str | None]
    cohort: Mapped[str | None]

    treatment_description: Mapped[str]
    off_treatment: Mapped[YNU]
    off_treatment_reason: Mapped[OffTreatmentReason | None]
    off_treatment_reason_other: Mapped[str | None]

    participant: Mapped[ParticipantORM] = relationship(back_populates="treatments", cascade="all, delete")
    adverse_events: Mapped[List[AdverseEventORM]] = relationship(back_populates="treatment", cascade="all, delete")

    therapy_agent_doses: Mapped[List[TherapyAgentDoseORM]] = relationship(
        back_populates="treatment", cascade="all, delete"
    )
    radiotherapy_doses: Mapped[List[RadiotherapyDoseORM]] = relationship(
        back_populates="treatment", cascade="all, delete"
    )
    surgeries: Mapped[List[SurgeryORM]] = relationship(back_populates="treatment", cascade="all, delete")
    stem_cell_transplants: Mapped[List[StemCellTransplantORM]] = relationship(
        back_populates="treatment", cascade="all, delete"
    )
