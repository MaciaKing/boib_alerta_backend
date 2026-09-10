from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
import jwt
from sqlalchemy.orm import Session
import pdb
from app.database.database import get_db
from app.models.user import User
from app.models.education import Education
from .schemas import UserCreate, UserOut
from .security import (
    ALGORITHM,
    SECRET_KEY,
    get_current_user,
    get_password_hash,
    verify_password,
)

users = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@users.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(
    user_in: UserCreate, 
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo electrónico ya está registrado."
        )

    hashed_pwd = get_password_hash(user_in.password)

    new_user = User(
        name=user_in.name,
        email=user_in.email,
        hashed_password=hashed_pwd
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@users.post("/token")
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


@users.post("/associate_education", status_code=status.HTTP_201_CREATED)
def user_associate_education(
    id_education: Annotated[int, Body(embed=True)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    
    new_education = db.get(Education, id_education)
    if not new_education:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Education with [id_education={id_education}] not found"
        )
    
    if new_education in current_user.educations:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Relation alredy exists"
        )
    
    current_user.educations.append(new_education)
    db.commit()
    
    return {"detail": "Succesfully created"}


@users.get("/me")
def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)]
):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "educations": [edu.to_dict() for edu in current_user.educations]
    }


@users.delete("/associate_education", status_code=status.HTTP_201_CREATED)
def user_associate_delete_education(
    id_education: Annotated[int, Body(embed=True)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):

    education = db.get(Education, id_education)
    if not education:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Education with [id_education={id_education}] not found"
        )
    
    if education not in current_user.educations:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user does not have this education associated"
        )
        
    current_user.educations.remove(education)
    db.commit()
    
    return {"detail": "Succesfully disassociated"}
