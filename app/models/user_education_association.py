from sqlalchemy import ForeignKey, String, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.education import Education
    
class UserEducationAssociation(Base):
    __tablename__ = "user_educations_association"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    education_id: Mapped[int] = mapped_column(
        ForeignKey("educations.id", ondelete="CASCADE"), primary_key=True
    )

    # Relaciones directas con los modelos
    user: Mapped["User"] = relationship(back_populates="education_associations")
    education: Mapped["Education"] = relationship(back_populates="user_associations")