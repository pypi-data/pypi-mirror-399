from __future__ import annotations
from pydantic import NonNegativeInt
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cidc_api.models.db.stage2.base_orm import BaseORM
from cidc_api.models.types import (
    CTCAEEventTerm,
    CTCAEEventCode,
    SeverityGradeSystem,
    SeverityGradeSystemVersion,
    SeverityGrade,
    SystemOrganClass,
    AttributionCause,
    AttributionLikelihood,
    YNU,
)


class AdverseEventORM(BaseORM):
    __tablename__ = "adverse_event"
    __repr_attrs__ = ["adverse_event_id", "participant_id", "event_term"]
    __table_args__ = {"schema": "stage2"}
    __data_category__ = "adverse_event"

    adverse_event_id: Mapped[int] = mapped_column(primary_key=True)
    participant_id: Mapped[int] = mapped_column(ForeignKey("stage2.participant.participant_id", ondelete="CASCADE"))
    treatment_id: Mapped[int | None] = mapped_column(ForeignKey("stage2.treatment.treatment_id", ondelete="CASCADE"))

    event_term: Mapped[CTCAEEventTerm | None]
    event_code: Mapped[CTCAEEventCode | None]
    severity_grade_system: Mapped[SeverityGradeSystem]
    severity_grade_system_version: Mapped[SeverityGradeSystemVersion]
    severity_grade: Mapped[SeverityGrade]
    event_other_specify: Mapped[str | None]
    system_organ_class: Mapped[SystemOrganClass | None]
    discontinuation_due_to_event: Mapped[bool]
    days_to_onset_of_event: Mapped[NonNegativeInt]
    days_to_resolution_of_event: Mapped[NonNegativeInt | None]
    serious_adverse_event: Mapped[YNU]
    dose_limiting_toxicity: Mapped[YNU]
    attribution_cause: Mapped[AttributionCause]
    attribution_likelihood: Mapped[AttributionLikelihood]
    individual_therapy: Mapped[str | None]

    participant: Mapped[ParticipantORM] = relationship(back_populates="adverse_events", cascade="all, delete")
    treatment: Mapped[TreatmentORM] = relationship(back_populates="adverse_events", cascade="all, delete")
