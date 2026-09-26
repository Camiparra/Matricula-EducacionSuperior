# components/charts.py
"""
Construcción de visualizaciones interactivas con Plotly.
Cada función recibe el DataFrame (ya filtrado) y devuelve un fragmento HTML
(<div>...</div>) listo para insertarse en el template con `{{ grafico | safe }}`.
"""

import plotly.express as px
import pandas as pd
from config import COLUMNS

PLOTLY_CONFIG = {"displaylogo": False, "responsive": True}
TEMPLATE = "plotly_white"


def _to_html(fig):
    return fig.to_html(full_html=False, include_plotlyjs=False, config=PLOTLY_CONFIG)


# ---------- Dimensión poblacional ----------
def grafico_barras_categoria(df: pd.DataFrame, titulo="Distribución por categoría"):
    col = COLUMNS["categoria_1"]
    if col not in df.columns or df.empty:
        return "<p class='text-muted'>Sin datos suficientes para graficar.</p>"
    conteo = df[col].value_counts().reset_index()
    conteo.columns = [col, "registros"]
    fig = px.bar(conteo, x=col, y="registros", title=titulo, template=TEMPLATE)
    return _to_html(fig)


def grafico_torta_categoria(df: pd.DataFrame, titulo="Participación por categoría"):
    col = COLUMNS["categoria_1"]
    if col not in df.columns or df.empty:
        return "<p class='text-muted'>Sin datos suficientes para graficar.</p>"
    conteo = df[col].value_counts().reset_index()
    conteo.columns = [col, "registros"]
    fig = px.pie(conteo, names=col, values="registros", title=titulo, template=TEMPLATE)
    return _to_html(fig)


# ---------- Dimensión territorial ----------
def grafico_barras_territorio(df: pd.DataFrame, top_n=15, titulo="Registros por territorio"):
    col = COLUMNS["territorial"]
    if col not in df.columns or df.empty:
        return "<p class='text-muted'>Sin datos suficientes para graficar.</p>"
    conteo = df[col].value_counts().nlargest(top_n).reset_index()
    conteo.columns = [col, "registros"]
    fig = px.bar(conteo, x="registros", y=col, orientation="h", title=titulo, template=TEMPLATE)
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    return _to_html(fig)


def grafico_treemap_territorio(df: pd.DataFrame, titulo="Concentración territorial"):
    col = COLUMNS["territorial"]
    if col not in df.columns or df.empty:
        return "<p class='text-muted'>Sin datos suficientes para graficar.</p>"
    conteo = df[col].value_counts().reset_index()
    conteo.columns = [col, "registros"]
    fig = px.treemap(conteo, path=[col], values="registros", title=titulo, template=TEMPLATE)
    return _to_html(fig)


# ---------- Dimensión temporal ----------
def grafico_linea_tiempo(df: pd.DataFrame, titulo="Evolución en el tiempo"):
    col = COLUMNS["temporal"]
    if col not in df.columns or df.empty:
        return "<p class='text-muted'>Sin datos suficientes para graficar.</p>"
    serie = df.copy()
    if pd.api.types.is_datetime64_any_dtype(serie[col]):
        serie["periodo"] = serie[col].dt.to_period("M").astype(str)
    else:
        serie["periodo"] = serie[col].astype(str)
    conteo = serie.groupby("periodo").size().reset_index(name="registros")
    fig = px.line(conteo, x="periodo", y="registros", markers=True, title=titulo, template=TEMPLATE)
    return _to_html(fig)


def grafico_barras_periodo(df: pd.DataFrame, titulo="Registros por periodo"):
    col = COLUMNS["temporal"]
    if col not in df.columns or df.empty:
        return "<p class='text-muted'>Sin datos suficientes para graficar.</p>"
    serie = df.copy()
    if pd.api.types.is_datetime64_any_dtype(serie[col]):
        serie["periodo"] = serie[col].dt.year
    else:
        serie["periodo"] = serie[col]
    conteo = serie.groupby("periodo").size().reset_index(name="registros")
    fig = px.bar(conteo, x="periodo", y="registros", title=titulo, template=TEMPLATE)
    return _to_html(fig)


# ---------- Dimensión multivariada ----------
def grafico_barras_agrupadas(df: pd.DataFrame, titulo="Relación entre dos variables categóricas"):
    col_a, col_b = COLUMNS["categoria_1"], COLUMNS["categoria_2"]
    if col_a not in df.columns or col_b not in df.columns or df.empty:
        return "<p class='text-muted'>Sin datos suficientes para graficar.</p>"
    conteo = df.groupby([col_a, col_b]).size().reset_index(name="registros")
    fig = px.bar(conteo, x=col_a, y="registros", color=col_b, barmode="group", title=titulo, template=TEMPLATE)
    return _to_html(fig)


def grafico_heatmap(df: pd.DataFrame, titulo="Mapa de calor entre variables"):
    col_a, col_b = COLUMNS["categoria_1"], COLUMNS["categoria_2"]
    if col_a not in df.columns or col_b not in df.columns or df.empty:
        return "<p class='text-muted'>Sin datos suficientes para graficar.</p>"
    tabla = pd.crosstab(df[col_a], df[col_b])
    fig = px.imshow(tabla, title=titulo, template=TEMPLATE, aspect="auto")
    return _to_html(fig)


def grafico_dispersión_numerica(df: pd.DataFrame, titulo="Relación con la variable numérica"):
    col_a, col_num = COLUMNS["categoria_1"], COLUMNS["numerica"]
    if col_a not in df.columns or col_num not in df.columns or df.empty:
        return "<p class='text-muted'>Sin datos suficientes para graficar.</p>"
    fig = px.box(df, x=col_a, y=col_num, title=titulo, template=TEMPLATE)
    return _to_html(fig)
