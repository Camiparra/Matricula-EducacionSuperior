# components/data_loader.py
"""
Componente encargado de cargar el conjunto de datos una sola vez (cache en
memoria), transformarlo al formato que necesita el resto de la app, y
aplicar los filtros interactivos que llegan desde cada tablero (querystring
de la petición GET).
"""

import os
import pandas as pd
from config import DATASET_PATH, COLUMNS, FECHA_FORMATO

_cache = {"df": None}

# Columnas de niveles de formación tal como vienen en el CSV original del MEN
_NIVELES_FORMACION = [
    "TECNICA PROFESIONAL",
    "TECNOLOGICA",
    "UNIVERSITARIA",
    "ESPECIALIZACION",
    "MAESTRIA",
    "DOCTORADO",
]

# El archivo del MEN trae en "Nombre del Departamento" el mismo código que en
# "Código delDepartamento" (parece un error de la fuente: la columna que
# debería traer el nombre en realidad repite el código). Se reconstruye el
# nombre real a partir del código DANE de departamento.
_DANE_DEPARTAMENTOS = {
    "05": "Antioquia", "08": "Atlántico", "11": "Bogotá D.C.", "13": "Bolívar",
    "15": "Boyacá", "17": "Caldas", "18": "Caquetá", "19": "Cauca", "20": "Cesar",
    "23": "Córdoba", "25": "Cundinamarca", "27": "Chocó", "41": "Huila",
    "44": "La Guajira", "47": "Magdalena", "50": "Meta", "52": "Nariño",
    "54": "Norte de Santander", "63": "Quindío", "66": "Risaralda",
    "68": "Santander", "70": "Sucre", "73": "Tolima", "76": "Valle del Cauca",
    "81": "Arauca", "85": "Casanare", "86": "Putumayo",
    "88": "Archipiélago de San Andrés, Providencia y Santa Catalina",
    "91": "Amazonas", "94": "Guainía", "95": "Guaviare", "97": "Vaupés",
    "99": "Vichada",
}


def load_dataset() -> pd.DataFrame:
    """Carga el dataset desde disco, lo transforma y lo cachea en memoria."""
    if _cache["df"] is not None:
        return _cache["df"]

    if not os.path.exists(DATASET_PATH):
        raise FileNotFoundError(
            f"No se encontró el archivo de datos en '{DATASET_PATH}'. "
            "Verifica que el CSV esté dentro de /data y que DATASET_PATH en "
            "config.py apunte al nombre correcto."
        )

    ext = os.path.splitext(DATASET_PATH)[1].lower()
    if ext in (".xlsx", ".xls"):
        raw = pd.read_excel(DATASET_PATH, dtype={"Código delDepartamento": str})
    else:
        # thousands="." interpreta "63.098" como número. Se fuerza el código
        # de departamento a texto para no perder ceros a la izquierda (ej. "05").
        raw = pd.read_csv(
            DATASET_PATH,
            sep=",",
            thousands=".",
            encoding="utf-8-sig",
            dtype={"Código delDepartamento": str},
        )

    raw.columns = [c.strip() for c in raw.columns]

    df = _transformar_a_formato_largo(raw)

    # Normaliza la columna temporal a datetime SOLO si config.py define un
    # formato de fecha explícito. Para este dataset (año como entero),
    # FECHA_FORMATO es None y este bloque no hace nada.
    col_temporal = COLUMNS.get("temporal")
    if col_temporal in df.columns and FECHA_FORMATO:
        df[col_temporal] = pd.to_datetime(
            df[col_temporal], format=FECHA_FORMATO, errors="coerce"
        )

    _cache["df"] = df
    return df


def _transformar_a_formato_largo(raw: pd.DataFrame) -> pd.DataFrame:
    """
    Adaptador específico del dataset "MEN Estadísticas Matrícula por
    Municipios ES".

    Hace dos cosas sobre el archivo original:

    1. Reconstruye el nombre real del departamento a partir del código DANE
       (la columna "Nombre del Departamento" del archivo viene con el código
       numérico repetido, no con el nombre).
    2. "Despivota" (pandas.melt) las 6 columnas de niveles de formación en
       una columna categórica (nivel_formacion) + una numérica
       (matriculados), y agrega periodo_quinquenio como segunda variable
       categórica para el análisis multivariado.

    Si el equipo cambia de dataset más adelante, esta función se puede
    reemplazar; el resto de la app solo depende de los nombres de columna
    definidos en config.COLUMNS, no de esta lógica interna.
    """
    columnas_requeridas = {"AÑO", "Código delDepartamento", "Nombre del Municipio"}
    if not columnas_requeridas.issubset(set(raw.columns)):
        # Dataset distinto al esperado: se devuelve tal cual. En ese caso
        # hay que ajustar config.COLUMNS a mano con los nombres reales.
        return raw

    raw = raw.copy()

    codigo = raw["Código delDepartamento"].astype(str).str.strip()
    codigo = codigo.where(codigo != "-", other=pd.NA)
    codigo_padded = codigo.str.zfill(2)
    raw["departamento"] = codigo_padded.map(_DANE_DEPARTAMENTOS).fillna("Sin dato")

    niveles_presentes = [c for c in _NIVELES_FORMACION if c in raw.columns]

    largo = raw.melt(
        id_vars=["AÑO", "departamento", "Nombre del Municipio"],
        value_vars=niveles_presentes,
        var_name="nivel_formacion",
        value_name="matriculados",
    )

    largo = largo.rename(columns={
        "AÑO": "anio",
        "Nombre del Municipio": "municipio",
    })

    largo["anio"] = pd.to_numeric(largo["anio"], errors="coerce")
    largo["matriculados"] = pd.to_numeric(largo["matriculados"], errors="coerce").fillna(0)
    largo["nivel_formacion"] = largo["nivel_formacion"].str.title()
    largo["municipio"] = largo["municipio"].str.title()

    bordes = [2004, 2009, 2014, 2019, 2025]
    etiquetas = ["2005-2009", "2010-2014", "2015-2019", "2020-2021"]
    largo["periodo_quinquenio"] = pd.cut(
        largo["anio"], bins=bordes, labels=etiquetas
    ).astype(str)

    return largo


def get_filter_options(df: pd.DataFrame, column: str, limit: int = 40):
    """Devuelve los valores únicos de una columna para poblar un <select> de filtro."""
    if column not in df.columns:
        return []
    valores = df[column].dropna().astype(str).unique().tolist()
    valores.sort()
    return valores[:limit]


def apply_filters(df: pd.DataFrame, filtros: dict) -> pd.DataFrame:
    """
    Aplica filtros interactivos sobre el DataFrame.
    `filtros` es un dict {nombre_columna: valor_seleccionado}. Ignora valores
    vacíos ("" o None), que representan la opción "Todos".
    """
    resultado = df.copy()
    for columna, valor in filtros.items():
        if valor and columna in resultado.columns:
            resultado = resultado[resultado[columna].astype(str) == str(valor)]
    return resultado
