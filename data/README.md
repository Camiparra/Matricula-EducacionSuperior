# Carpeta /data

## Archivo actual

`MEN_ESTADISTICAS_MATRICULA_POR_MUNICIPIOS_ES_20260925.csv`

Matrícula de educación superior por municipio, publicado por el Ministerio
de Educación Nacional (MEN). Descargado de:
https://www.datos.gov.co/Educaci-n/MEN_ESTADISTICAS-MATRICULA-POR-MUNICIPIOS_ES/y9ga-zwzy/about_data

- **Registros originales:** 19.618 filas, 12 columnas
- **Cobertura temporal:** 2005–2021
- **Cobertura territorial:** 33 departamentos + Bogotá D.C., 1.361 municipios

Ficha completa en el `README.md` de la raíz del repositorio.

## Ya resuelto en el código — no repetir el trabajo

`components/data_loader.py` ya se encarga de:

1. Reconstruir el nombre real del departamento (el archivo trae el código
   DANE repetido en la columna `Nombre del Departamento` en vez del nombre).
2. Transformar el archivo de formato ancho a formato largo (`pandas.melt`),
   generando `nivel_formacion` (categórica) y `matriculados` (numérica) a
   partir de las 6 columnas de niveles de formación.
3. Agregar `periodo_quinquenio` como segunda variable categórica.

Si necesitas los datos crudos tal como vienen del MEN (sin transformar),
puedes cargarlos directamente con `pandas.read_csv(..., thousands=".")` fuera
de la app; pero para los tableros de las 4 dimensiones, usa siempre
`components.data_loader.load_dataset()`, que ya entrega el dataframe listo.
