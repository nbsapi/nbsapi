from functools import wraps
from typing import List

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from nbsapi.database import get_db_session

from . import Base


class AdaptationTarget(Base):
    __tablename__ = "adaptationtarget"
    id: Mapped[int] = mapped_column(primary_key=True)
    target: Mapped[str] = mapped_column(index=True, unique=True)
    solutions: Mapped[List["Association"]] = relationship(
        back_populates="tg", lazy="joined"
    )
