from datetime import datetime, timedelta, timezone
import os
import time
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm  # <-- Corregido el origen de la importación
import jwt
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from .schemas import UserCreate, UserOut
from .security import (
    ALGORITHM,
    SECRET_KEY,
    get_current_user,
    get_password_hash,
    verify_password,
)

app = FastAPI()


@app.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(
    user_in: UserCreate, 
    db: Session = Depends(get_db)
):
    # 1. Comprobar si el usuario ya existe por su email
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo electrónico ya está registrado."
        )

    # 2. Hashear la contraseña antes de guardarla
    hashed_pwd = get_password_hash(user_in.password)

    # 3. Crear el nuevo objeto User de SQLAlchemy
    new_user = User(
        name=user_in.name,
        email=user_in.email,
        hashed_password=hashed_pwd
    )

    # 4. Guardar en la base de datos
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # 5. Devolver el nuevo usuario
    return new_user


@app.post("/token")
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    to_encode = {"sub": user.email, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return {"access_token": encoded_jwt, "token_type": "bearer"}

    
# Endpoint /me que devuelve la información personal del usuario autenticado
@app.get("/me")
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)]
):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email
    }


# Ejemplo de otro endpoint protegido
@app.get("/items/")
async def read_items(
    current_user: Annotated[User, Depends(get_current_user)]
):
    return {
        "user_email": current_user.email,
        "items": ["Item 1", "Item 2"]
    }