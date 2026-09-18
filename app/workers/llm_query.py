import json
import pdfplumber
import ollama

# 1. Instanciar el cliente indicando el nombre del servicio Docker
client = ollama.Client(host='http://ollama:11434')

def extraer_texto_pdf(ruta_pdf):
    """Extrae el texto de todas las páginas del PDF."""
    texto_completo = ""
    with pdfplumber.open(ruta_pdf) as pdf:
        for pagina in pdf.pages:
            texto = pagina.extract_text()
            if texto:
                texto_completo += texto + "\n"
    return texto_completo

def procesar_boib_con_ollama(ruta_pdf):
    # Convertir el PDF a string
    print("Extrayendo texto del PDF...")
    texto_pdf = extraer_texto_pdf(ruta_pdf)

    # Definir el prompt con el sistema de extracción y el esquema JSON
    prompt_sistema = """
Eres un sistema de extracción de datos automatizado especializado en el BOIB (Butlletí Oficial de les Illes Balears). Tu única función es leer el texto oficial introducido y mapearlo en un objeto JSON estructurado con precisión quirúrgica.

REGLAS DE EXTRACCIÓN Y OBLIGACIONES:
1. IDIOMA DEL TEXTO: El texto de entrada estará en catalán o español. Debes analizarlo sin importar la lengua de origen.
2. VALORES NULL: Si una clave JSON no aparece mencionada explícitamente en el texto, debes asignar `null` o `false` según corresponda. JAMÁS inventes, asumas o deduzcas datos que no figuren en el texto.
3. FORMATO DE SALIDA: Responde ÚNICAMENTE con el objeto JSON válido. No incluyas explicaciones, ni textos como "Aquí tienes el JSON", ni bloques de código adicionales fuera de la estructura.

ESQUEMA JSON OBLIGATORIO:
{
  "datos_generales": {
    "organismo_convocante": "string | null",
    "titulo_convocatoria": "string | null",
    "codigo_referencia_oficial": "string | null"
  },
  "tipo_procedimiento": {
    "categoria_proceso": "oferta_empleo_publico" | "bolsa_empleo" | "comision_servicios" | "libre_designacion" | "adscripcion_provisional" | "movilidad_interadministrativa" | null,
    "sistema_seleccion": "oposicion" | "concurso" | "concurso_oposicion" | "valoracion_meritos" | "entrevista" | null,
    "turno": "libre" | "promocion_interna" | "discapacidad" | "movilidad" | null,
    "es_interinidad": boolean
  },
  "caracteristicas_puesto": {
    "grupo_clasificacion": "A1" | "A2" | "B" | "C1" | "C2" | "AP" | null,
    "escala_subescala_cuerpo": "string | null",
    "num_plazas": number | null,
    "plazas_reservadas_discapacidad": number | null,
    "ubicacion_municipio": "string | null"
  },
  "requisitos_especificos": {
    "nivel_catalan_exigido": "A2" | "B1" | "B2" | "C1" | "C2" | "LAE" | null,
    "catalan_es_requisito_o_merito": "requisito" | "merito" | "exento_con_plazo" | null,
    "experiencia_previa_requerida": {
      "requiere_experiencia": boolean,
      "meses_minimos": number | null
    },
    "carnes_conducir": ["string"],
    "otros_requisitos_habilitantes": ["string"]
  },
  "fases_y_mecanica": {
    "requiere_examen_presencial": boolean,
    "tipo_pruebas": ["test" | "caso_practico" | "desarrollo_teorico" | "fisicas" | "psicotecnico" | "catalan"],
    "crea_nueva_bolsa_de_trabajo": boolean,
    "orden_bolsa_por": "nota_examen" | "baremo_meritos" | "ambos" | null
  },
  "plazos_y_tramitacion": {
    "plazo_presentacion_dias": number | null,
    "tipo_dias_plazo": "habiles" | "naturales" | null,
    "inicio_computo": "dia_siguiente_boib" | "dia_siguiente_boe" | null,
    "requiere_tasa_examen": boolean,
    "importe_tasa_euros": number | null,
    "enlace_tramitacion_telematica": "string | null"
  }
}
"""

    prompt_usuario = f"""
---
TEXTO DEL BOIB A ANALIZAR:
\"\"\"
{texto_pdf}
\"\"\"
"""

    print("Analizando texto con Ollama (llama3.2)...")

    # 2. Llamada usando la instancia 'client' configurada
    respuesta = client.chat(
        model="llama3.2",
        messages=[
            {"role": "system", "content": prompt_sistema},
            {"role": "user", "content": prompt_usuario}
        ],
        format="json",
        options={
            "temperature": 0.0
        }
    )

    contenido = respuesta['message']['content']

    # Convertir la cadena a diccionario de Python
    datos_json = json.loads(contenido)
    return datos_json


if __name__ == "__main__":
    archivo_pdf = "9279.pdf"

    try:
        resultado = procesar_boib_con_ollama(archivo_pdf)
        
        # Imprimir resultado por consola
        print("\n--- RESULTADO EXTRAÍDO EN JSON ---")
        print(json.dumps(resultado, indent=2, ensure_ascii=False))
        
        # Guardar en archivo
        with open("resultado_boib.json", "w", encoding="utf-8") as f:
            json.dump(resultado, f, indent=2, ensure_ascii=False)
            
    except Exception as e:
        print(f"Error procesando el PDF o en la llamada a Ollama: {e}")