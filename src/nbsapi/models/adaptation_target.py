from __future__ import annotations

from typing import TYPE_CHECKING
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from . import Base

if TYPE_CHECKING:
    from .naturebasedsolution import Association


class AdaptationTarget(Base):
    __tablename__ = "adaptationtarget"
    id: Mapped[int] = mapped_column(primary_key=True)
    target: Mapped[str] = mapped_column(index=True, unique=True)
    solutions: Mapped[list[Association]] = relationship(
        back_populates="tg", lazy="joined"
    )
