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

 Crea un fichero Excel con 5000 encuestas en `data/raw/encuestas_YYYYMM.xlsx`.

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
**Periodo:** 2025-10-01 → 2025-10-31
**Generado:** 2025-11-09 22:51:32.997256

## Distribución 1–10 (%)
 |    |           |       1 |        2 |        3 |        4 |        5 |        6 |        7 |       8 |        9 |       10 |
|---:|:----------|--------:|---------:|---------:|---------:|---------:|---------:|---------:|--------:|---------:|---------:|
|  0 | Atención  | 9.87561 | 10.2069  |  9.55592 |  9.88142 | 10.0326  |  9.82911 |  9.88142 | 10.0151 | 10.4859  | 10.236   |
|  1 | Soporte   | 9.98705 |  9.83992 |  9.73988 | 10.299   | 10.1342  | 10.2519  |  9.94586 |  9.9694 |  9.98705 |  9.84581 |
|  2 | Ventas    | 9.95034 |  9.84983 | 10.0449  | 10.447   |  9.89713 | 10.0568  | 10.1691  | 10.1632 |  9.67837 |  9.74341 |
|  3 | Marketing | 9.11314 | 10.3709  |  9.82938 |  9.86432 |  9.72457 |  9.78862 | 10.4583  | 10.4059 | 10.4233  | 10.0215  |

## Calidad y cobertura

 **Filas iniciales:** 200000 
 **Filas en cuarentena:** 33802 
 **Filas finales:** 68283
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
