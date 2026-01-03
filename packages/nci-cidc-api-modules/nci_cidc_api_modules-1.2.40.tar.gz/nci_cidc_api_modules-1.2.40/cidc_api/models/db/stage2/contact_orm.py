from __future__ import annotations
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cidc_api.models.db.stage2.base_orm import BaseORM


class ContactORM(BaseORM):
    __tablename__ = "contact"
    __table_args__ = {"schema": "stage2"}

    contact_id: Mapped[int] = mapped_column(primary_key=True)
    institution_id: Mapped[int] = mapped_column(ForeignKey("stage2.institution.institution_id", ondelete="CASCADE"))
    shipment_from_id: Mapped[int | None] = mapped_column(ForeignKey("stage2.shipment.shipment_id", ondelete="CASCADE"))
    shipment_to_id: Mapped[int | None] = mapped_column(ForeignKey("stage2.shipment.shipment_id", ondelete="CASCADE"))

    name: Mapped[str | None]
    email: Mapped[str | None]
    phone: Mapped[str | None]
    street1: Mapped[str | None]
    street2: Mapped[str | None]
    city: Mapped[str | None]
    state: Mapped[str | None]
    zip: Mapped[str | None]
    country: Mapped[str | None]

    institution: Mapped[InstitutionORM | None] = relationship(back_populates="contacts", cascade="all, delete")
    shipment_from: Mapped[ShipmentORM] = relationship(cascade="all, delete", foreign_keys=[shipment_from_id])
    shipment_to: Mapped[ShipmentORM] = relationship(cascade="all, delete", foreign_keys=[shipment_to_id])
