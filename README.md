# Análisis de Población — Matrícula en Educación Superior (Colombia)

Aplicación web (Flask + Bootstrap) para el análisis exploratorio de la
matrícula de educación superior por municipio en Colombia, usando datos del
Portal Nacional de Datos Abiertos, organizada en cuatro dimensiones:
**poblacional, territorial, temporal y relacional/multivariada**.

## Integrantes y responsabilidades

| # | Integrante | Correo | Responsabilidad técnica | Dimensión asignada |
|---|------------|--------|---------------------------|----------------------|
| 1 | Camila Parra Berrio | cparrab@ucundinamarca.edu.co | Administración del repositorio (estructura, ramas, revisión de PRs) | Poblacional |
| 2 | Jonathan David Chavarro Segura | jdchavarro@ucundinamarca.edu.co | Estructura del proyecto Flask + Bootstrap | Territorial |
| 3 | Nicolas Suarez Rativa | nsuarezr@ucundinamarca.edu.co | Preparación y publicación en Render | Temporal |
| 4 | Richard Ludim Barajas Parrado | rlbarajas@ucundinamarca.edu.co | Informe técnico en PDF | Relacional y multivariada |

## Conjunto de datos

| Campo | Valor |
|---|---|
| Nombre | MEN Estadísticas Matrícula por Municipios ES |
| Tema | Matrícula en educación superior |
| Población estudiada | Estudiantes matriculados en educación superior en Colombia, agregados por municipio y año |
| Entidad que publica | Ministerio de Educación Nacional (MEN) — SNIES |
| URL original | https://www.datos.gov.co/Educaci-n/MEN_ESTADISTICAS-MATRICULA-POR-MUNICIPIOS_ES/y9ga-zwzy/about_data |
| Archivo en el repo | `data/MEN_ESTADISTICAS_MATRICULA_POR_MUNICIPIOS_ES_20260925.csv` |
| Registros (archivo original) | 19.618 filas |
| Registros (tras transformar a formato largo) | 117.708 filas |
| Cobertura temporal | 2005 a 2021 |
| Cobertura territorial | 33 departamentos + Bogotá D.C. (36 códigos de departamento en el archivo, 3 sin nombre asignable), 1.361 municipios |

### Nota sobre la calidad del dato original

El archivo original trae dos particularidades que ya están resueltas en
`components/data_loader.py`, no hace falta corregirlas de nuevo:

1. **Departamento sin nombre real**: la columna `Nombre del Departamento`
   del CSV en realidad repite el código DANE en vez del nombre. Se
   reconstruyó el nombre real a partir de una tabla de códigos DANE
   (`_DANE_DEPARTAMENTOS` en `data_loader.py`). 72 filas no tienen un código
   válido y quedan marcadas como `"Sin dato"`.
2. **Formato ancho**: cada nivel de formación (técnica, tecnológica,
   universitaria, especialización, maestría, doctorado) venía como su
   propia columna numérica. Se transformó a formato largo con
   `pandas.melt`, generando una columna categórica real `nivel_formacion` y
   su numérica asociada `matriculados`. También se agregó
   `periodo_quinquenio` (2005-2009, 2010-2014, 2015-2019, 2020-2021) como
   segunda variable categórica para los cruces multivariados.

El resultado final que usa el resto de la app tiene estas columnas:
`anio`, `departamento`, `municipio`, `nivel_formacion`, `matriculados`,
`periodo_quinquenio` — mapeadas en `config.py → COLUMNS`.

## Estructura del repositorio

```
.
├── README.md
├── CONTRIBUTING.md        # reglas para la integración del trabajo (leer antes de programar)
├── LICENSE
├── .gitignore
├── .github/
│   └── PULL_REQUEST_TEMPLATE.md
├── app.py                 # rutas Flask (una por dimensión)
├── config.py               # ruta del dataset + mapeo de columnas
├── requirements.txt
├── Procfile                # comando de arranque para Render
├── render.yaml              # blueprint opcional de Render
├── deploy.ps1               # script de apoyo para el despliegue (PowerShell)
├── components/                # lógica reutilizable del backend
│   ├── data_loader.py          # carga, adapta y filtra el dataset
│   ├── kpis.py                  # cálculo de indicadores por dimensión
│   └── charts.py                 # construcción de gráficas (Plotly)
├── data/
│   └── MEN_ESTADISTICAS_MATRICULA_POR_MUNICIPIOS_ES_20260925.csv
├── static/
│   ├── css/style.css
│   └── js/main.js
└── templates/
    ├── base.html            # layout + navbar + footer
    ├── macros.html           # componentes reutilizables (tarjetas KPI, filtros)
    ├── index.html
    ├── poblacional.html
    ├── territorial.html
    ├── temporal.html
    └── multivariada.html
```

## Puesta en marcha local

```bash
python -m venv venv
# Windows:
venv\Scripts\Activate.ps1
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
python app.py
```

La app queda disponible en `http://127.0.0.1:5000`. El dataset ya está
conectado — no hace falta configurar nada para probarla localmente.

## Flujo de trabajo en GitHub

Antes de programar, lee **[CONTRIBUTING.md](./CONTRIBUTING.md)** completo:
ahí están las reglas de ramas, commits, pull requests y los criterios de
revisión que el Integrante 1 aplica a cada PR. Resumen rápido:

```bash
git checkout main
git pull origin main
git checkout -b feature/dimension-<tu-dimension>
# ... desarrollar el tablero ...
git add .
git commit -m "feat: tablero de la dimension <tu-dimension>"
git push origin feature/dimension-<tu-dimension>
# Abrir Pull Request hacia main y solicitar revisión al Integrante 1
```

Ramas esperadas: `feature/dimension-poblacional`,
`feature/dimension-territorial`, `feature/dimension-temporal`,
`feature/dimension-multivariada`. Mínimo 3 commits descriptivos por
integrante.

## Despliegue en Render

1. Crear cuenta en [render.com](https://render.com) y conectar el repositorio de GitHub.
2. **New + → Web Service** (o **Blueprint** usando `render.yaml`).
3. Configuración manual si no se usa el Blueprint:
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn app:app`
   - Runtime: Python 3
4. Cada `git push` a `main` dispara un nuevo despliegue automático.
5. El Integrante 3 puede usar `deploy.ps1` para automatizar la instalación
   local, la validación de archivos y el `commit + push` hacia `main`:

   ```powershell
   .\deploy.ps1              # instala, valida y hace push
   .\deploy.ps1 -RunLocal    # además prueba la app localmente antes de publicar
   ```

## Checklist de cada tablero (dimensión)

- [ ] Título de la dimensión y pregunta de análisis
- [ ] Descripción de las variables utilizadas
- [ ] Tres indicadores (KPIs)
- [ ] Tres visualizaciones generadas a partir del dataset real
- [ ] Dos filtros interactivos
- [ ] Interpretación de cada visualización
- [ ] Tres conocimientos evidentes (Pregunta, Variables, Procedimiento,
      Evidencia, Hallazgo, Interpretación, Utilidad, Limitación)
- [ ] Una limitación del análisis
- [ ] Una decisión sustentada en los datos

## Estado actual

- [x] Repositorio estructurado (app Flask + gobernanza) en un solo lugar
- [x] Rama principal `main` configurada
- [x] Reglas de integración documentadas (`CONTRIBUTING.md`)
- [x] Dataset descargado, validado y conectado a la app (`config.py` + `data_loader.py`)
- [x] Rutas base de las 4 dimensiones funcionando con datos reales (KPIs, gráficas y filtros de ejemplo)
- [ ] Repositorio subido a GitHub y colaboradores agregados
- [ ] Interpretaciones y conocimientos evidentes redactados por cada integrante
- [ ] Aplicación publicada en Render
- [ ] Informe técnico en PDF
