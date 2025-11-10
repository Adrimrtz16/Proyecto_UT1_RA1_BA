---
title: "Proceso ETL de Encuestas de Satisfacción"
tags: ["UT1","RA1","docs"]
version: "1.0.0"
owner: "Adrián Martínez Díaz"
status: "finished"
---
# 1. Objetivo

El objetivo de este proyecto es generar, limpiar y almacenar datos simulados de encuestas de satisfacción de distintas áreas de una empresa.
El proceso implementa un flujo ETL (Extracción, Transformación y Carga) completamente automatizado mediante scripts en Python que generan los datos, los depuran y los almacenan en distintos formatos (CSV, SQLite y Parquet).
Además, se produce un reporte resumen en formato Markdown con las estadísticas por área y nivel de satisfacción.

# 2. Alcance

**Cubre:**

- Generación de un dataset sintético con registros de encuestas.
- Validación y limpieza de los campos `age`, `satisfaction` y `comment`.
- Ingesta de datos a múltiples formatos: CSV, SQLite y Parquet.
- Cálculo de métricas y generación de reportes.

**No cubre:**

- Conexión a fuentes de datos reales.
- Análisis estadístico avanzado o visualizaciones.
- Automatización en entornos de producción (cron jobs, pipelines, etc.).

# 3. Decisiones / Reglas

- **Estrategia de ingestión:** batch único ejecutado manualmente.
- **Calidad de datos:**
  - Se eliminan registros con `age` o `satisfaction` nulos.
  - Solo se conservan encuestas de mayores de 18 años.
  - `satisfaction` válido entre 1 y 10.
  - Los valores fuera de rango se mueven a una tabla de *cuarentena*.
- **Normalización de texto:** los comentarios se convierten a minúsculas, sin tildes ni espacios.
- **Reproducibilidad:** se generan ficheros con fecha en su nombre.

# 4. Procedimiento / Pasos

1. **Generación de datos (get_data.py):**
```bash
python get_data.py
```

 Crea un fichero Excel con encuestas en `data/raw/encuestas_YYYYMM.xlsx`.

 Ejecución del proceso ETL (run.py):

 ```bash
 python run.py
 ```

 Este script realiza las siguientes etapas:

 - Conversión de Excel → CSV (`data/drops/<fecha>/encuestas_raw.csv`).
 - Ingesta y validación de tipos de datos.
 - Limpieza y filtrado de valores inválidos.
 - Creación de tablas SQLite (`output/sql/encuestas.db`).
 - Exportación del dataset limpio a Parquet (`output/parquet/clean_encuestas.parquet`).
 - Generación de reporte en Markdown (`output/report/reporte.md`).

 ## 5. Evidencias

 Archivos generados:

 - `data/raw/encuestas_YYYYMM.xlsx`
 - `data/drops/<fecha>/encuestas_raw.csv`
 - `data/drops/<fecha>/encuestas_cuarentena.csv`
 - `data/drops/<fecha>/encuestas_limpias.csv`
 - `output/sql/encuestas.db`
 - `output/parquet/clean_encuestas.parquet`
 - `output/report/reporte.md`

 Ejemplo de salida del reporte:

 ```markdown
# Reporte · Encuestas de Satisfacción
**Periodo:** 2025-10-01 → 2025-10-30
**Generado:** 2025-11-10 17:26:16.551041

## Distribución 1–10 (%)
 |    |           |        1 |       2 |        3 |        4 |        5 |        6 |        7 |        8 |        9 |       10 |
|---:|:----------|---------:|--------:|---------:|---------:|---------:|---------:|---------:|---------:|---------:|---------:|
|  0 | Atención  |  9.65196 | 10.0465 |  9.86397 | 10.1054  |  9.94641 |  9.98763 |  9.82863 | 10.2409  |  9.93463 | 10.394   |
|  1 | Soporte   | 10.2213  | 10.5023 | 10.4496  | 10.1862  |  9.78808 | 10.1159  |  9.99298 |  9.47781 |  9.71783 |  9.54806 |
|  2 | Ventas    | 10.2727  | 10.2668 |  9.93108 |  9.83095 |  9.90752 |  9.87218 | 10.2197  | 10.096   |  9.84273 |  9.76026 |
|  3 | Marketing |  9.73504 | 10.3206 |  9.72912 |  9.75869 | 10.0544  | 10.1964  | 10.0899  | 10.0662  | 10.0662  |  9.98344 |

## Calidad y cobertura

 **Filas iniciales:** 200000 
 **Filas en cuarentena:** 34175 
 **Filas finales:** 67948

## Medias por departamento

 **Atención:** 5.53  
 **Soporte:** 5.42  
 **Ventas:** 5.47  
 **Marketing:** 5.52
 ```

 ## 6. Resultados

 Volumen inicial: 200.000 encuestas.

 Datos eliminados: encuestas con edad < 18 o satisfacción fuera de 1–10.

 Duración del proceso: el tiempo total se guarda en la columna `_ingest_ts`.

 Fuentes finales:

 - Tablas SQL: `Raw`, `Quarantine`, `Clean`.
 - Dataset limpio exportado en formato Parquet para análisis posterior.
 - Reporte automatizado con distribución de satisfacción por área.

 ## 7. Lecciones aprendidas

 - Separar claramente las etapas (generación, ingestión, limpieza, almacenamiento) facilita el mantenimiento.
 - Los datos generados aleatoriamente pueden incluir valores atípicos (edades negativas, satisfacción >10), lo que obligó a definir reglas de validación.
 - La modularidad del flujo permite adaptarlo fácilmente a fuentes reales en el futuro.

 ## 8. Próximos pasos

 - Implementar validaciones automáticas previas a la ingesta.
 - Incluir visualizaciones en el reporte (matplotlib / seaborn).
 - Automatizar el proceso con cron o Airflow.
 - Añadir pruebas unitarias para las funciones críticas (`limpiar_texto`, validaciones numéricas).
