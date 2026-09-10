from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.associationproxy import association_proxy, AssociationProxy
from app.database.database import Base
from app.models.user_education_association import UserEducationAssociation

import json

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    name: Mapped[str] = mapped_column(
        String(500),
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True, 
        index=True, 
        nullable=False
    )

    hashed_password: Mapped[str] = mapped_column(
        String(255), nullable=False
    )
    
    # Relación técnica con la tabla intermedia
    education_associations: Mapped[list["UserEducationAssociation"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )

    # ACCESO DIRECTO: Devuelve list[Education]
    educations: AssociationProxy[list["Education"]] = association_proxy(
        "education_associations",
        "education",
        creator=lambda edu_obj: UserEducationAssociation(education=edu_obj)
    )
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email
        }
    
    def to_json(self):
        return json.dumps(self.to_dict())
    