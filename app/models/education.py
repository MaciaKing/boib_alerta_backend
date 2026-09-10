from app.database.database import Base
from sqlalchemy import DateTime, String, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum
import json
from sqlalchemy.ext.associationproxy import association_proxy, AssociationProxy
from sqlalchemy.orm import Mapped, mapped_column

class EducationLevel(enum.Enum):
    FP_BASICA = "FP Básica"
    FP_MEDIO = "FP Grado Medio"
    FP_SUPERIOR = "FP Grado Superior"
    GRADO = "Grado Universitario"
    MASTER = "Máster"
    DOCTORADO = "Doctorado"

class Education(Base):
    __tablename__ = "educations"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )
    
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=True,
    )
    
    level: Mapped[EducationLevel] = mapped_column(
        Enum(EducationLevel),
        nullable=False,
    )
        
    family: Mapped[str] = mapped_column(String(100), nullable=True)
    
    # Relación técnica con la tabla intermedia
    user_associations: Mapped[list["UserEducationAssociation"]] = relationship(
        back_populates="education",
        cascade="all, delete-orphan"
    )
    
    # ACCESO DIRECTO: Devuelve list[User]
    users: AssociationProxy[list["User"]] = association_proxy(
        "user_associations",
        "user"
    )
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            # Si level es un Enum, extraemos su string (.value); si es None, lo dejamos
            "level": self.level.value if isinstance(self.level, EducationLevel) else self.level,
            "family": self.family
        }
    
    def to_json(self):
        return json.dumps(self.to_dict())