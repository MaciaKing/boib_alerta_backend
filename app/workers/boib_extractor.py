import re
from bs4 import BeautifulSoup
import requests

from app.database.database import SessionLocal
from app.models.convocatoria import Convocatoria
from app.models.organismo import Organismo

BASE_URL = "https://www.caib.es"
url = "https://www.caib.es/eboibfront/"


# 1. Obtener última publicación
def get_last_publication_url():
    req = requests.get(url)
    soup = BeautifulSoup(req.text, 'html.parser')
    tabla = soup.select('table a.ordinario')
    return tabla[-1]['href']


# 2. Buscar ESPECÍFICAMENTE el enlace a "Secció II" (Autoritats i personal)
def get_seccio_ii_url(last_pub_href):
    full_url = url + last_pub_href.split('/eboibfront/')[1]
    req = requests.get(full_url)
    soup = BeautifulSoup(req.text, 'html.parser')

    # Buscamos el enlace a la Secció II de forma dinámica
    enlace_seccio_2 = soup.find(
        'a', text=re.compile(r'Secció II|Autoritats i personal', re.I)
    )

    if not enlace_seccio_2:
        enlace_seccio_2 = soup.find(
            lambda tag: tag.name == 'a'
            and 'seccio-ii' in tag.get('href', '').lower()
        )

    return enlace_seccio_2['href'] if enlace_seccio_2 else None


# 3. Ejecución del proceso
last_pub = get_last_publication_url()
seccio_ii_href = get_seccio_ii_url(last_pub)

if not seccio_ii_href:
    print("❌ No se pudo encontrar el enlace a la Secció II.")
else:
    url_final = (
        BASE_URL + seccio_ii_href
        if not seccio_ii_href.startswith('http')
        else seccio_ii_href
    )
    print(f"Descargando Secció II desde: {url_final}")

    req_final = requests.get(url_final)
    soup = BeautifulSoup(req_final.text, 'html.parser')

    # 4. Buscar el H3 de "Subsecció segona. Oposicions i concursos"
    titulo_objetivo = soup.find(
        lambda tag: tag.name == 'h3'
        and 'Oposicions i concursos' in tag.get_text()
    )

    if titulo_objetivo:
        print(f"✅ Encontrado: {titulo_objetivo.get_text(strip=True)}")

        # Coger del título para abajo (la lista ul.entitats)
        lista_ul = titulo_objetivo.find_next('ul', class_='entitats')

        if lista_ul:
            elementos_li = lista_ul.find_all('li', recursive=False)
            print(f"Se han encontrado {len(elementos_li)} convocatorias.\n")

            db = SessionLocal()

            try:
                for li in elementos_li:
                    # Extraer Organismo
                    org_tag = li.find('h3', class_='organisme')
                    if not org_tag:
                        continue
                    organisme = org_tag.get_text(strip=True)

                    # Extraer Descripción
                    resolucion_li = li.find('ul', class_='resolucions')
                    if not resolucion_li:
                        continue
                    text_descriptiu = resolucion_li.find('p').get_text(
                        strip=True
                    )

                    # Extraer Enlace HTML
                    html_link = li.select_one('a.html')
                    url_anuncio = html_link['href'] if html_link else None

                    print(f"Organismo: {organisme}")
                    print(f"Texto: {text_descriptiu}")

                    # --- GUARDADO EN BASE DE DATOS ---

                    # 1. Buscar o crear Organismo
                    organismo_db = (
                        db.query(Organismo)
                        .filter(Organismo.nombre == organisme)
                        .first()
                    )

                    if organismo_db is None:
                        organismo_db = Organismo(nombre=organisme)
                        db.add(organismo_db)
                        db.flush()  # Asigna un ID antes del commit

                    # 2. Crear Convocatoria asociada
                    new_convocatoria = Convocatoria(
                        organismo_id=organismo_db.id,
                        descripcion=text_descriptiu,
                        url=url_anuncio,
                    )
                    db.add(new_convocatoria)
                    print("--> Registrado en BD correctamente\n")

                # Guardar todos los cambios acumulados
                db.commit()

            except Exception as e:
                db.rollback()
                print(f"❌ Error guardando en base de datos: {e}")
            finally:
                db.close()
        else:
            print("No se encontró la lista 'ul.entitats' debajo del título.")
    else:
        print(
            "❌ No se encontró el título 'Subsecció segona. Oposicions i concursos'."
        )