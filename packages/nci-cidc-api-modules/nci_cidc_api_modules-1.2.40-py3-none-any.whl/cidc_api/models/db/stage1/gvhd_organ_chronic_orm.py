from __future__ import annotations
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cidc_api.models.db.stage1.base_orm import BaseORM
from cidc_api.models.types import GVHDOrgan, GVHDOrganChronicScore


class GVHDOrganChronicORM(BaseORM):
    __tablename__ = "gvhd_organ_chronic"
    __repr_attrs__ = ["gvhd_organ_chronic_id", "organ"]
    __table_args__ = {"schema": "stage1"}
    __data_category__ = "gvhd_organ_chronic"

    gvhd_organ_chronic_id: Mapped[int] = mapped_column(primary_key=True)
    gvhd_diagnosis_chronic_id: Mapped[int] = mapped_column(
        ForeignKey("stage1.gvhd_diagnosis_chronic.gvhd_diagnosis_chronic_id", ondelete="CASCADE")
    )
    organ: Mapped[GVHDOrgan]
    chronic_score: Mapped[GVHDOrganChronicScore]

    diagnosis: Mapped[GVHDDiagnosisChronicORM] = relationship(back_populates="organs", cascade="all, delete")
