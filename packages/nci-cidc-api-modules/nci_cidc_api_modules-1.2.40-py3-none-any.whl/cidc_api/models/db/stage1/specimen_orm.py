from __future__ import annotations
from datetime import datetime
from typing import List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cidc_api.models.db.stage1.base_orm import BaseORM
from cidc_api.models.types import (
    UberonAnatomicalTerm,
    ICDO3MorphologicalCode,
    SpecimenType,
    SpecimenDescription,
    TumorType,
    CollectionProcedure,
    FixationStabilizationType,
    PrimaryContainerType,
    VolumeUnits,
    ProcessedType,
    ConcentrationUnits,
    DerivativeType,
    PBMCRestingPeriodUsed,
    MaterialUnits,
    MaterialStorageCondition,
    QCCondition,
    ReplacementRequested,
    ResidualUse,
    DiagnosisVerification,
    AssayType,
)


class SpecimenORM(BaseORM):
    __tablename__ = "specimen"
    __repr_attrs__ = ["specimen_id", "participant_id", "cimac_id"]
    __table_args__ = {"schema": "stage1"}

    specimen_id: Mapped[int] = mapped_column(primary_key=True)
    participant_id: Mapped[int] = mapped_column(ForeignKey("stage1.participant.participant_id", ondelete="CASCADE"))

    cimac_id: Mapped[str]
    collection_event_name: Mapped[str]
    days_to_specimen_collection: Mapped[int]
    organ_site_of_collection: Mapped[UberonAnatomicalTerm]

    participant: Mapped[ParticipantORM] = relationship(back_populates="specimens", cascade="all, delete")
