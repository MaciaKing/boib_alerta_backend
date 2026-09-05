import requests
from app.models.organismo import Organismo
from app.models.convocatoria import Convocatoria
from app.database.database import SessionLocal
from bs4 import BeautifulSoup
import re

BASE_URL = "https://www.caib.es"
url = "https://www.caib.es/eboibfront/"


def last_publication_page():
    req = requests.get(url)
    soup = BeautifulSoup(str(req.text), 'html.parser')
    tabla = soup.select('table a.ordinario')
    last_publication = tabla[-1]['href']
    return last_publication

last_publication = last_publication_page()
print(f"last publication {last_publication}")


## Last publication day
def last_publication_autoritats_i_personal_url():
    last_publication_day_url = url + last_publication.split('/eboibfront/')[1]
    req_last_publication = requests.get(last_publication_day_url)
    soup = BeautifulSoup(str(req_last_publication.text), 'html.parser')
    # Get principal menu of last publication day
    lista_menu = soup.select("a[rel='section']")
    # Select autoritats i personal menu of last publication day
    return lista_menu[1]['href']

autoritats_i_personal_last_publication = last_publication_autoritats_i_personal_url()


## Last publication day of autoritats i personal
def soup_of_last_publication_day_autoritats_i_personals():
    last_publication_day_autoritats_i_personal_url = BASE_URL + autoritats_i_personal_last_publication
    req_last_publication_day_autoritats_i_personal = requests.get(last_publication_day_autoritats_i_personal_url)
    soup = BeautifulSoup(str(req_last_publication_day_autoritats_i_personal.text), 'html.parser')
    return soup

soup = soup_of_last_publication_day_autoritats_i_personals()


# Ahora tengo que filtrar para coger todo lo de despues de Oposicions i concursos
# Las que ponen en la descripcion Resolucio, no me sirven. Ya que estas son correccion d'errades.
# Contractacio, convocatoria, bases especifiques, Contractacio de personal laboral fix, borsa, 
#
# <ul class="entitats">. La lista de 

titulo_objetivo = soup.find('h3', string=re.compile(r"Oposicions i concursos"))

if titulo_objetivo:
    # 2. Buscamos el primer 'ul' con clase 'entitats' que esté DESPUÉS de ese h3
    lista_ul = titulo_objetivo.find_next('ul', class_='entitats')
    
    if lista_ul:
        # 3. Obtenemos solo los 'li' directos de esa lista
        elementos_li = lista_ul.find_all('li', recursive=False)
        print(f"Se han encontrado {len(elementos_li)} elementos.\n")
        
        db = SessionLocal()

        for li in elementos_li:
            organisme = li.find('h3', class_='organisme').get_text(strip=True)
            text_descriptiu = li.find_next('p')
            print(f"Organismo: {organisme}")
            print(f"Texto: {text_descriptiu.text}")

            # Search if de organism exist
            organismo_db = db.query(Organismo).filter(
                Organismo.nombre == organisme
            ).first()

            # if not exist
            if organismo_db is None:
                organismo_db = Organismo(
                nombre=organisme
            )
            db.add(organismo_db)
            db.flush()

            new_convocatioria = Convocatoria(
                organismo_id = organismo_db.id,
                descripcion = text_descriptiu.text
            )
            db.add(new_convocatioria)
            db.commit()
            print()
            
    else:
        print("No se encontró la lista 'ul.entitats' debajo del título.")
else:
    print("No se encontró ningún título que contenga 'Oposicions i concursos'.")

