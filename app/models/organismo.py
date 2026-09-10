from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base
import json

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
    
    convocatorias: Mapped[list["Convocatoria"]] = relationship("Convocatoria", back_populates="organismo")
        
    def to_dict(self):
            return {
                "id": self.id,
                "name": self.nombre
            }
        
    def to_json(self):
        return json.dumps(self.to_dict())