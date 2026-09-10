import pandas as pd
import os
from app.database.database import SessionLocal, engine, Base
from app.models.education import Education, EducationLevel
from app.models.user import User
from app.models.user_education_association import UserEducationAssociation
from app.api.security import get_password_hash
from sqlalchemy import select
import pdb


Base.metadata.create_all(bind=engine)
db = SessionLocal()

# Diccionario para mapear los textos del CSV al Enum
LEVEL_MAPPER = {
    "Grado Medio": EducationLevel.FP_MEDIO,
    "Grado Superior": EducationLevel.FP_SUPERIOR,
    "FP Básica": EducationLevel.FP_BASICA,
    "Grado Universitario": EducationLevel.GRADO
}

df_fp = pd.read_csv("app/database/data/titulaciones_fp.csv", sep=';', encoding="utf-8")
df_grado = pd.read_csv("app/database/data/titulaciones_grado.csv", sep=';', encoding="utf-8")
df = pd.concat([df_grado, df_fp])

try:
    ### CREATE BASIC EDUCATIONS ###
    if db.query(Education).first() is not None:
        print("La tabla 'educations' ya contiene datos. Cancelando inserción.")
    else:
        educations_to_add = []
        for index, row in df.iterrows():
            # Obtener el valor del Enum correspondiente
            raw_level = row["nivel"]
            enum_level = LEVEL_MAPPER.get(raw_level)

            if not enum_level:
                raise ValueError(f"El nivel '{raw_level}' en la fila {index} no se encuentra en LEVEL_MAPPER.")

            new_education = Education(
                name=row["nombre_oficial"],
                level=enum_level,  # Pasar el objeto Enum
                family=row["familia_profesional"]
            )
            educations_to_add.append(new_education)

        db.add_all(educations_to_add)
        db.commit()

    ### CREATE BASIC USER ###
    first_user = User(
        name = os.getenv("FIRST_USER_NAME"),
        email = os.getenv("FIRST_USER_EMAIL"),
        hashed_password = get_password_hash(os.getenv("FIRST_USER_PASSWORD"))
    )
    
    db.add(first_user)
    db.commit()
    
    ## Search Grado en informatica
    stmt = select(Education).where(Education.name == "Grado en Ingeniería Informática")
    education_ing_informatica = db.scalar(stmt)
    
    ## Relation for the first user 544
    uea = UserEducationAssociation(
        user_id = first_user.id,
        education_id = education_ing_informatica.id
    )
    
    db.add(uea)
    db.commit()
    
    pdb.set_trace()

except Exception as e:
    db.rollback()
    print(f"Error al insertar datos: {e}")

finally:
    db.close()