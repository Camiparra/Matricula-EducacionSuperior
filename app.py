# app.py
"""
Aplicación Flask principal.
Integrante 2 configura este archivo y las rutas iniciales de las 4 dimensiones.
Cada integrante (3 quien despliega, 1/poblacional, 2/territorial, etc.) puede
ajustar la lógica de SU dimensión dentro de components/kpis.py y components/charts.py
sin tener que tocar las rutas de los demás.
"""

from flask import Flask, render_template, request
from config import DATASET_INFO, COLUMNS, PORT, DEBUG
from components.data_loader import load_dataset, get_filter_options, apply_filters
from components import kpis, charts

app = Flask(__name__)


@app.context_processor
def inject_globals():
    """Disponible en todos los templates sin tener que pasarlo en cada render_template."""
    return {"dataset_info": DATASET_INFO}


@app.route("/")
def index():
    try:
        df = load_dataset()
        total_registros = len(df)
        dataset_ok = True
    except FileNotFoundError:
        total_registros = 0
        dataset_ok = False
    return render_template("index.html", total_registros=total_registros, dataset_ok=dataset_ok)


# ---------------------------------------------------------------------------
# Dimensión 1: Poblacional (Integrante 1)
# ---------------------------------------------------------------------------
@app.route("/poblacional")
def poblacional():
    df = load_dataset()

    filtro_categoria = request.args.get("categoria", "")
    filtro_territorio = request.args.get("territorio", "")
    df_filtrado = apply_filters(df, {
        COLUMNS["categoria_1"]: filtro_categoria,
        COLUMNS["territorial"]: filtro_territorio,
    })

    contexto = {
        "kpis": kpis.kpis_poblacionales(df_filtrado),
        "grafico_1": charts.grafico_barras_categoria(df_filtrado),
        "grafico_2": charts.grafico_torta_categoria(df_filtrado),
        "opciones_categoria": get_filter_options(df, COLUMNS["categoria_1"]),
        "opciones_territorio": get_filter_options(df, COLUMNS["territorial"]),
        "filtro_categoria": filtro_categoria,
        "filtro_territorio": filtro_territorio,
        "registros_filtrados": len(df_filtrado),
    }
    return render_template("poblacional.html", **contexto)


# ---------------------------------------------------------------------------
# Dimensión 2: Territorial (Integrante 2)
# ---------------------------------------------------------------------------
@app.route("/territorial")
def territorial():
    df = load_dataset()

    filtro_territorio = request.args.get("territorio", "")
    filtro_periodo = request.args.get("periodo", "")
    df_filtrado = apply_filters(df, {
        COLUMNS["territorial"]: filtro_territorio,
    })
    if filtro_periodo and COLUMNS["temporal"] in df_filtrado.columns:
        col_temp = COLUMNS["temporal"]
        if str(df_filtrado[col_temp].dtype).startswith("datetime"):
            df_filtrado = df_filtrado[df_filtrado[col_temp].dt.year.astype(str) == filtro_periodo]
        else:
            df_filtrado = df_filtrado[df_filtrado[col_temp].astype(str) == filtro_periodo]

    contexto = {
        "kpis": kpis.kpis_territoriales(df_filtrado),
        "grafico_1": charts.grafico_barras_territorio(df_filtrado),
        "grafico_2": charts.grafico_treemap_territorio(df_filtrado),
        "opciones_territorio": get_filter_options(df, COLUMNS["territorial"]),
        "filtro_territorio": filtro_territorio,
        "filtro_periodo": filtro_periodo,
        "registros_filtrados": len(df_filtrado),
    }
    return render_template("territorial.html", **contexto)


# ---------------------------------------------------------------------------
# Dimensión 3: Temporal (Integrante 3)
# ---------------------------------------------------------------------------
@app.route("/temporal")
def temporal():
    df = load_dataset()

    filtro_territorio = request.args.get("territorio", "")
    filtro_categoria = request.args.get("categoria", "")
    df_filtrado = apply_filters(df, {
        COLUMNS["territorial"]: filtro_territorio,
        COLUMNS["categoria_1"]: filtro_categoria,
    })

    contexto = {
        "kpis": kpis.kpis_temporales(df_filtrado),
        "grafico_1": charts.grafico_linea_tiempo(df_filtrado),
        "grafico_2": charts.grafico_barras_periodo(df_filtrado),
        "opciones_territorio": get_filter_options(df, COLUMNS["territorial"]),
        "opciones_categoria": get_filter_options(df, COLUMNS["categoria_1"]),
        "filtro_territorio": filtro_territorio,
        "filtro_categoria": filtro_categoria,
        "registros_filtrados": len(df_filtrado),
    }
    return render_template("temporal.html", **contexto)


# ---------------------------------------------------------------------------
# Dimensión 4: Relacional y multivariada (Integrante 4)
# ---------------------------------------------------------------------------
@app.route("/multivariada")
def multivariada():
    df = load_dataset()

    filtro_categoria = request.args.get("categoria", "")
    filtro_territorio = request.args.get("territorio", "")
    df_filtrado = apply_filters(df, {
        COLUMNS["categoria_1"]: filtro_categoria,
        COLUMNS["territorial"]: filtro_territorio,
    })

    contexto = {
        "kpis": kpis.kpis_multivariados(df_filtrado),
        "grafico_1": charts.grafico_barras_agrupadas(df_filtrado),
        "grafico_2": charts.grafico_heatmap(df_filtrado),
        "grafico_3": charts.grafico_dispersión_numerica(df_filtrado),
        "opciones_categoria": get_filter_options(df, COLUMNS["categoria_1"]),
        "opciones_territorio": get_filter_options(df, COLUMNS["territorial"]),
        "filtro_categoria": filtro_categoria,
        "filtro_territorio": filtro_territorio,
        "registros_filtrados": len(df_filtrado),
    }
    return render_template("multivariada.html", **contexto)


if __name__ == "__main__":
    # Ejecución local: python app.py
    app.run(host="0.0.0.0", port=PORT, debug=DEBUG)
