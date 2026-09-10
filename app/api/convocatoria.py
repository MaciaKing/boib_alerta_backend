from fastapi import APIRouter, Depends,status, Query
from app.database.database import get_db
from app.models.convocatoria import Convocatoria
from app.models.organismo import Organismo
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, func
import math
import pdb

convocatoria = APIRouter(
    prefix="/convocatoria",
    tags=["Convocatoria"]
)

@convocatoria.get("/all", status_code=status.HTTP_200_OK)
def read_all_convocatoria(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    offset = (page - 1) * limit

    total_records = db.scalar(select(func.count()).select_from(Convocatoria)) or 0

    # Carga la relación 'organismo' en una sola consulta SQL optimizada
    statement = (
        select(Convocatoria)
        #.options(joinedload(Convocatoria.organismo))
        .offset(offset)
        .limit(limit)
    )
    
    convocatorias = db.scalars(statement).all()
    
    return [
        {
            **c.to_dict(),
            "organismo": c.organismo.to_dict() if c.organismo else None
        }
        for c in convocatorias
    ]

    