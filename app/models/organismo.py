from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from app.database.database import Base

class Organismo(Base):
    __tablename__ = "organismos"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    nombre: Mapped[str] = mapped_column(
        String(500),
        unique=True,
        nullable=False,
    )