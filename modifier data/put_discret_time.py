import pandas as pd
from datetime import datetime

df = pd.read_csv("./modifier data/202207-bluebikes-tripdata.csv")

df['temp_date'] = pd.to_datetime(df['starttime'], format='%Y-%m-%d %H:%M:%S.%f')

reference_date = datetime(2022, 7, 1, 0, 0, 0)

# Calculer les secondes écoulées
df['discret_time'] = ((df['temp_date'] - reference_date).dt.total_seconds()).astype(int)
for i in range(10):
    print(df['discret_time'][i])
# Sauvegarder le DataFrame avec la nouvelle colonne dans un fichier CSV
df.to_csv('./modifier data/202207-bluebikes-tripdata.csv', index=False)

print("Colonne ajoutée avec succès!")
