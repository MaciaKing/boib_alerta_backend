from datetime import datetime

from sqlalchemy import DateTime, String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class Convocatoria(Base):
    __tablename__ = "convocatorias"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    descripcion: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    organismo_id: Mapped[int] = mapped_column(
        ForeignKey("organismos.id"),
        nullable=False,
    )

    url: Mapped[str | None] = mapped_column(
        String(1000),
        unique=True,
        nullable=True,
    )