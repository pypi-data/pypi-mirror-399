from __future__ import annotations
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cidc_api.models.db.stage2.base_orm import BaseORM
from cidc_api.models.types import ICD10CMCode, ICD10CMTerm


class ComorbidityORM(BaseORM):
    __tablename__ = "comorbidity"
    __repr_attrs__ = ["comorbidity_id", "comorbidity_term"]
    __table_args__ = {"schema": "stage2"}
    __data_category__ = "comorbidity"

    comorbidity_id: Mapped[int] = mapped_column(primary_key=True)
    medical_history_id: Mapped[int] = mapped_column(
        ForeignKey("stage2.medical_history.medical_history_id", ondelete="CASCADE")
    )

    comorbidity_code: Mapped[ICD10CMCode | None]
    comorbidity_term: Mapped[ICD10CMTerm | None]
    comorbidity_other: Mapped[str | None]

    medical_history: Mapped[MedicalHistoryORM] = relationship(back_populates="comorbidities", cascade="all, delete")
