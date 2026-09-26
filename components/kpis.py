# components/kpis.py
"""
Cálculo de los tres indicadores mínimos que exige cada tablero
(ver 'Requisitos de cada dimensión' en la guía del proyecto).
Cada función devuelve una lista de dicts {"titulo", "valor", "detalle"}
lista para pintar como tarjetas (KPI cards) en el template.
"""

import pandas as pd
from config import COLUMNS


def kpis_poblacionales(df: pd.DataFrame):
    col_cat = COLUMNS["categoria_1"]
    total = len(df)
    if col_cat not in df.columns or total == 0:
        return _kpis_vacios()

    conteo = df[col_cat].value_counts()
    categoria_top = conteo.index[0] if len(conteo) else "N/D"
    porcentaje_top = round((conteo.iloc[0] / total) * 100, 1) if len(conteo) else 0

    return [
        {"titulo": "Total de registros", "valor": f"{total:,}", "detalle": "Tamaño de la población analizada"},
        {"titulo": "Categorías distintas", "valor": df[col_cat].nunique(), "detalle": f"Variable: {col_cat}"},
        {"titulo": "Categoría predominante", "valor": categoria_top, "detalle": f"{porcentaje_top}% del total"},
    ]


def kpis_territoriales(df: pd.DataFrame):
    col_terr = COLUMNS["territorial"]
    total = len(df)
    if col_terr not in df.columns or total == 0:
        return _kpis_vacios()

    conteo = df[col_terr].value_counts()
    territorio_top = conteo.index[0] if len(conteo) else "N/D"
    participacion = round((conteo.iloc[0] / total) * 100, 1) if len(conteo) else 0

    return [
        {"titulo": "Territorios distintos", "valor": df[col_terr].nunique(), "detalle": f"Variable: {col_terr}"},
        {"titulo": "Territorio con más registros", "valor": territorio_top, "detalle": f"{participacion}% del total"},
        {"titulo": "Registros sin territorio", "valor": int(df[col_terr].isna().sum()), "detalle": "Datos incompletos"},
    ]


def kpis_temporales(df: pd.DataFrame):
    col_temp = COLUMNS["temporal"]
    total = len(df)
    if col_temp not in df.columns or total == 0:
        return _kpis_vacios()

    serie = df[col_temp].dropna()
    if pd.api.types.is_datetime64_any_dtype(serie) and len(serie):
        rango = f"{serie.min().date()} a {serie.max().date()}"
        por_periodo = df.groupby(df[col_temp].dt.to_period("M")).size()
    else:
        rango = f"{serie.min()} a {serie.max()}" if len(serie) else "N/D"
        por_periodo = df.groupby(col_temp).size()

    periodo_pico = str(por_periodo.idxmax()) if len(por_periodo) else "N/D"

    return [
        {"titulo": "Rango temporal", "valor": rango, "detalle": f"Variable: {col_temp}"},
        {"titulo": "Periodos distintos", "valor": len(por_periodo), "detalle": "Agrupación disponible"},
        {"titulo": "Periodo con más registros", "valor": periodo_pico, "detalle": "Pico identificado"},
    ]


def kpis_multivariados(df: pd.DataFrame):
    col_a, col_b = COLUMNS["categoria_1"], COLUMNS["categoria_2"]
    total = len(df)
    if col_a not in df.columns or col_b not in df.columns or total == 0:
        return _kpis_vacios()

    combinaciones = df.groupby([col_a, col_b]).size().sort_values(ascending=False)
    combinacion_top = combinaciones.index[0] if len(combinaciones) else ("N/D", "N/D")

    return [
        {"titulo": "Combinaciones posibles", "valor": df[col_a].nunique() * df[col_b].nunique(), "detalle": f"{col_a} × {col_b}"},
        {"titulo": "Combinaciones observadas", "valor": len(combinaciones), "detalle": "En los datos reales"},
        {"titulo": "Combinación más frecuente", "valor": f"{combinacion_top[0]} / {combinacion_top[1]}", "detalle": f"{combinaciones.iloc[0]} registros" if len(combinaciones) else ""},
    ]


def _kpis_vacios():
    return [
        {"titulo": "Sin datos", "valor": "-", "detalle": "Configura config.py y coloca el dataset en /data"},
        {"titulo": "Sin datos", "valor": "-", "detalle": ""},
        {"titulo": "Sin datos", "valor": "-", "detalle": ""},
    ]
