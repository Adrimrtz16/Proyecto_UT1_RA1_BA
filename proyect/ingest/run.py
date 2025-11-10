import pandas as pd
from pathlib import Path
from datetime import datetime
import time
import sqlite3

# Ruta base del proyecto
ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "drops" / datetime.now().strftime('%Y-%m-%d')
OUTPUT = ROOT / "output"
OUTPUT.mkdir(parents=True, exist_ok=True)

# Iniciar el cronómetro de _ingest_ts
start_time = time.time()

# =============================================================
#                       EXCEL A CSV
# =============================================================
previous_month = pd.Timestamp.now() - pd.DateOffset(months=1)
excel_route = ROOT / 'data' / 'raw' / f'encuestas_{previous_month.strftime("%Y%m")}.xlsx'

todayDate = datetime.now().strftime('%Y-%m-%d')
destiny_dir = ROOT / 'data' / 'drops' / todayDate

destiny_dir.mkdir(parents=True, exist_ok=True)

ruta_csv = destiny_dir / 'encuestas_raw.csv'

df = pd.read_excel(excel_route)
df.to_csv(ruta_csv, index=False, encoding='utf-8')

# =============================================================
#                       INGESTA
# =============================================================
csv = DATA / "encuestas_raw.csv"

df = pd.read_csv(csv)

df["date"] = pd.to_datetime(df["date"])
df['age'] = pd.to_numeric(df['age'], errors='coerce')
df['satisfaction'] = pd.to_numeric(df['satisfaction'], errors='coerce')

output_csv = DATA / "encuestas_ingestadas.csv"
df.to_csv(output_csv, index=False, na_rep='NaN')

# =============================================================
#                       LIMPIEZA
# =============================================================
csv = DATA / "encuestas_ingestadas.csv"

df = pd.read_csv(csv)

df = df.dropna(subset=['age'])
df = df.dropna(subset=['satisfaction'])

def limpiar_texto(text):
    if pd.isna(text):
        return ""
    text = text.lower()
    replacements = {" ": "", "á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u"}
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text

df["comment"] = df["comment"].apply(limpiar_texto)

df['age'] = df['age'].astype(int)
df = df[df['age'] >= 18]

df['satisfaction'] = df['satisfaction'].astype(int)
removed_satisfaction_range = df[~((df['satisfaction'] >= 1) & (df['satisfaction'] <= 10))]
df = df[(df['satisfaction'] >= 1) & (df['satisfaction'] <= 10)]


output_csv = DATA / "encuestas_cuarentena.csv"
removed_satisfaction_range.to_csv(output_csv, index=False, na_rep='NaN')

# Detener el cronómetro de _ingest_ts
end_time = time.time()

elapsed_time = end_time - start_time

df["_ingest_ts"] = elapsed_time
df["_source_file"] = f'encuestas_{previous_month.strftime("%Y%m")}.xlsx'
df["_batch_id"] = pd.Timestamp.now()

output_csv = DATA / "encuestas_limpias.csv"
df.to_csv(output_csv, index=False, na_rep='NaN')

# =============================================================
#                       ALMACENAMIENTO
# =============================================================
csvRaw = DATA / "encuestas_raw.csv"
csvQuarantine = DATA / "encuestas_cuarentena.csv"
csvClean = DATA / "encuestas_limpias.csv"

dfRaw = pd.read_csv(csvRaw)
dfQuarantine = pd.read_csv(csvQuarantine)
dfClean = pd.read_csv(csvClean)

PATH_DB = OUTPUT / "sql" / "encuestas.db"
PATH_DB.parent.mkdir(parents=True, exist_ok=True)
conn = sqlite3.connect(PATH_DB)

# Si la base de datos ya existe, añadimos las filas nuevas.
def _to_sql_with_fallback(df, name, con):
    try:
        df.to_sql(name, con, if_exists='append', index=False)
    except Exception as e:
        df.to_sql(name, con, if_exists='replace', index=False)

_to_sql_with_fallback(dfRaw, "Raw", conn)
_to_sql_with_fallback(dfQuarantine, "Quarantine", conn)
_to_sql_with_fallback(dfClean, "Clean", conn)

conn.close()

# Guardar el DataFrame como archivo Parquet 
parquet_fname = f"clean_encuestas_{pd.Timestamp.now().strftime('%Y-%m-%d')}.parquet"
PARQUET_PATH = OUTPUT / "parquet" / parquet_fname
PARQUET_PATH.parent.mkdir(parents=True, exist_ok=True)
dfClean.to_parquet(PARQUET_PATH, index=False, engine="pyarrow")

# =============================================================
#                       REPORTES
# =============================================================
# Calcular el porcentaje dentro de cada área asegurando compatibilidad de índices
conteo = dfClean.groupby(['area', 'satisfaction']).size().reset_index(name='conteo')
conteo['porcentaje'] = conteo.groupby('area')['conteo'].transform(lambda x: x / x.sum() * 100)

# Crear el DataFrame dfReport con los porcentajes
areas = ["Atención", "Soporte", "Ventas", "Marketing"]
valores = {str(i): [] for i in range(1, 11)}

for area in areas:
    for satisfaction in range(1, 11):
        porcentaje = conteo.loc[(conteo['area'] == area) & (conteo['satisfaction'] == satisfaction), 'porcentaje']
        valores[str(satisfaction)].append(porcentaje.iloc[0] if not porcentaje.empty else 0)

dfReport = pd.DataFrame({"": areas, **valores})

# Calcular medias por departamento
medias = dfClean.groupby('area')['satisfaction'].mean().reindex(areas).fillna(0)
medias_fmt = {area: f"{medias.loc[area]:.2f}" for area in areas}

txt = (
    f"# Reporte · Encuestas de Satisfacción\n"
    f"**Periodo:** {dfClean['date'].iloc[0]} → {dfClean['date'].iloc[-1]}\n"
    f"**Generado:** {pd.Timestamp.now()}\n\n"
    f"## Distribución 1–10 (%)\n {dfReport.to_markdown()}\n\n"
    f"## Calidad y cobertura\n\n **Filas iniciales:** {dfRaw.shape[0]} \n **Filas en cuarentena:** {dfQuarantine.shape[0]} \n **Filas finales:** {dfClean.shape[0]}\n\n"
    f"## Medias por departamento\n\n"
    f" **Atención:** {medias_fmt['Atención']}  \n"
    f" **Soporte:** {medias_fmt['Soporte']}  \n"
    f" **Ventas:** {medias_fmt['Ventas']}  \n"
    f" **Marketing:** {medias_fmt['Marketing']}"
)

REPORT_PATH = ROOT / "output" / "report" / "reporte.md"
REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
with open(REPORT_PATH, "w", encoding="utf-8") as f:
    f.write(txt)











