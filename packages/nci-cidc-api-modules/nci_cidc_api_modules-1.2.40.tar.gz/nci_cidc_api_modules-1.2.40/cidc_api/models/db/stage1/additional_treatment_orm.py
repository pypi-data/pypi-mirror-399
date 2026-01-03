from __future__ import annotations
from pydantic import NonNegativeInt

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cidc_api.models.db.stage1.base_orm import BaseORM


class AdditionalTreatmentORM(BaseORM):
    __tablename__ = "additional_treatment"
    __repr_attrs__ = ["additional_treatment_id", "participant_id", "description"]
    __table_args__ = {"schema": "stage1"}
    __data_category__ = "additional_treatment"

    additional_treatment_id: Mapped[int] = mapped_column(primary_key=True)
    participant_id: Mapped[int] = mapped_column(ForeignKey("stage1.participant.participant_id", ondelete="CASCADE"))

    additional_treatment_days_to_start: Mapped[NonNegativeInt | None]
    additional_treatment_days_to_end: Mapped[NonNegativeInt | None]
    additional_treatment_description: Mapped[str]

    participant: Mapped["ParticipantORM"] = relationship(back_populates="additional_treatments", cascade="all, delete")
