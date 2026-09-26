# config.py
"""
Configuración central del proyecto.

Ya está conectado al dataset real del equipo (ver DATASET_INFO). Si en algún
momento cambian de conjunto de datos, solo hay que actualizar DATASET_PATH,
DATASET_INFO y COLUMNS — el resto de la app no necesita tocarse.
"""

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Archivo real, descargado de datos.gov.co
DATASET_PATH = os.path.join(
    BASE_DIR, "data", "MEN_ESTADISTICAS_MATRICULA_POR_MUNICIPIOS_ES_20260925.csv"
)

DATASET_INFO = {
    "nombre": "MEN Estadísticas Matrícula por Municipios ES",
    "tema": "Matrícula en educación superior",
    "poblacion": "Estudiantes matriculados en programas de educación superior en Colombia, agregados por municipio y año",
    "entidad": "Ministerio de Educación Nacional (MEN) — SNIES",
    "url_original": "https://www.datos.gov.co/Educaci-n/MEN_ESTADISTICAS-MATRICULA-POR-MUNICIPIOS_ES/y9ga-zwzy/about_data",
    "registros_estimados": 19618,
}

# Mapeo de columnas: la clave es el "rol" que cumple la columna en el
# análisis, el valor es el nombre de la columna YA TRANSFORMADA por
# components/data_loader.py (ver _transformar_a_formato_largo).
#
# El archivo original viene en formato ANCHO (un nivel de formación por
# columna: TECNICA PROFESIONAL, UNIVERSITARIA, etc.). data_loader.py lo
# convierte a formato LARGO antes de que el resto de la app lo use, para
# tener una columna categórica real (nivel_formacion) y una numérica
# (matriculados). Por eso los nombres de aquí abajo NO son los nombres
# literales del CSV original.
COLUMNS = {
    "territorial": "departamento",     # también existe 'municipio' si se quiere más detalle
    "temporal": "anio",                # entero (2005-2021), no es una fecha
    "categoria_1": "nivel_formacion",  # técnica profesional, tecnológica, universitaria, etc.
    "categoria_2": "periodo_quinquenio",  # 2005-2009, 2010-2014, 2015-2019, 2020-2021
    "numerica": "matriculados",
}

# La columna temporal ya es un año (entero), no una fecha con formato
# día/mes/año. Se deja en None para que data_loader.py NO intente
# convertirla con pandas.to_datetime.
FECHA_FORMATO = None

# Puerto local para pruebas (Render asigna su propio puerto en producción)
PORT = int(os.environ.get("PORT", 5000))
DEBUG = os.environ.get("FLASK_DEBUG", "1") == "1"
