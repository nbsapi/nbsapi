from __future__ import annotations

from typing import Any

from geoalchemy2 import Geometry, WKBElement
from sqlalchemy import ForeignKey, JSON, String, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base


class Association(Base):
    __tablename__ = "nbs_target_assoc"
    nbs_id: Mapped[int] = mapped_column(
        ForeignKey("naturebasedsolution.id"), primary_key=True
    )
    target_id: Mapped[int] = mapped_column(
        ForeignKey("adaptationtarget.id"), primary_key=True
    )
    tg = relationship("AdaptationTarget", lazy="joined", back_populates="solutions")

    solution = relationship("NatureBasedSolution", back_populates="solution_targets")
    value: Mapped[int]

    @property
    def target_obj(self):
        return self.tg


class NatureBasedSolution(Base):
    __tablename__ = "naturebasedsolution"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(index=True, unique=True)
    definition: Mapped[str] = mapped_column(index=True)
    cobenefits: Mapped[str] = mapped_column(index=True)
    specificdetails: Mapped[str] = mapped_column(index=True)
    location: Mapped[str] = mapped_column(index=True)
    geometry: Mapped[WKBElement] = mapped_column(
        Geometry("GEOMETRY", srid=4326), spatial_index=True, nullable=True
    )
    styling: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    physical_properties: Mapped[dict[str, Any] | None] = mapped_column(
        JSON, nullable=True, comment="Physical dimensions and properties"
    )
    measure_id: Mapped[str | None] = mapped_column(
        String,
        ForeignKey("measure_types.id"),
        nullable=True,
        comment="Reference to measure type",
    )
    area: Mapped[float | None] = mapped_column(
        Float, nullable=True, comment="Calculated area in square meters"
    )
    length: Mapped[float | None] = mapped_column(
        Float, nullable=True, comment="Calculated length in meters (for LineString)"
    )

    # Relationships
    measure_type = relationship("MeasureType", lazy="joined")
    solution_targets = relationship(
        "Association",
        back_populates="solution",
        lazy="joined",
        collection_class=list,
        cascade="all, delete-orphan",
    )
    impacts = relationship(
        "Impact",
        back_populates="solution",
        collection_class=list,
        lazy="selectin",
        cascade="all, delete-orphan",
    )
