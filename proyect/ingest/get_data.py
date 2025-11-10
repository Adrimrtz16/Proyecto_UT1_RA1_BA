import numpy as np
import random
import pandas as pd
from pathlib import Path

# random.seed(42)
# np.random.seed(42)

rows = 5000

typeAreas = ["Atención", "Soporte", "Ventas", "Marketing"]
typeComents = ["Excelente", "Buenisimo", " ", "Malo", "Horrible"]

ids = [f"R{str(i).zfill(6)}" for i in range(1, rows + 1)]
dates = pd.date_range(start='2025-10-01', end='2025-10-31', periods=rows).date
areas = np.random.choice(typeAreas, size=rows)
comments = np.random.choice(typeComents, size=rows)

ages = []
for _ in range(rows):
    if random.random() < 0.1:  
        ages.append(None)  
    else:
        ages.append(random.randint(-10,65))

satisfaction = []
for _ in range(rows):
    if random.random() < 0.1:  
        satisfaction.append("NS/NC")  
    else:
        satisfaction.append(random.randint(-2, 12))

df = pd.DataFrame({
  'id_respuesta': ids,    
  'date': dates,
  'age': ages,
  'area': areas,
  'satisfaction': satisfaction,
  'comment': comments
})

output_path_xlsx = Path('../data/raw')
output_path_xlsx.mkdir(parents=True, exist_ok=True)

previous_month = pd.Timestamp.now() - pd.DateOffset(months=1)

output_path = output_path_xlsx / f'encuestas_{previous_month.strftime("%Y%m")}.xlsx'
df.to_excel(output_path, index=False)

