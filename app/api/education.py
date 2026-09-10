from fastapi import APIRouter, Depends,status
from app.database.database import get_db
from app.models.education import Education
from sqlalchemy.orm import Session
from sqlalchemy import select

education = APIRouter(
    prefix="/education",
    tags=["Education"]
)

@education.get("/all", status_code=status.HTTP_200_OK,
    summary="Get all education degrees/qualifications.",
    description="Returns the complete catalog of education categories registered in the system to populate frontend select inputs.",
    response_description="Complete list of education objects."
)
def read_all_education(
    db: Session = Depends(get_db)
):
    statement = select(Education)
    
    all_educations = db.scalars(statement).all()
    
    return all_educations