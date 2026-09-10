from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from .security import get_current_user
from .users import users
from .education import education
from .convocatoria import convocatoria

app = FastAPI()

app.include_router(users)
app.include_router(education)
app.include_router(convocatoria)

@app.get("/items/")
def read_items(
    current_user: Annotated[User, Depends(get_current_user)]
):
    return {
        "user_email": current_user.email,
        "items": ["Item 1", "Item 2"]
    }