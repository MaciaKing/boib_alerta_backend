from sqlalchemy import DateTime, String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from zoneinfo import ZoneInfo
import datetime
import json
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
    
    time_created: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.datetime.now(ZoneInfo("Europe/Madrid")),
        server_default=func.now(),
        nullable=False
    )
    
    organismo: Mapped["Organismo"] = relationship("Organismo", back_populates="convocatorias")
        
    def to_dict(self, show_organisme_id=False):
        if show_organisme_id:
           return {
                "id": self.id,
                "descripcion": self.descripcion,
                "organismo_id": self.organismo_id,
                "url": self.url,
                "time_created": self.time_created.isoformat()
            }
        else: 
            return {
                "id": self.id,
                "descripcion": self.descripcion,
                "url": self.url,
                "time_created": self.time_created
            }
        
    def to_json(self):
        return json.dumps(self.to_dict())