import pandas as pd


# Charger le fichier CSV
df = pd.read_csv("./modifier data/202207-bluebikes-tripdata2.csv")

# Supprimer les colonnes
df = df.drop(columns=["start station name", "end station name"])

# Sauvegarder le fichier modifié
df.to_csv("./modifier data/202207-bluebikes-tripdata2.csv", index=False)

print("Colonnes supprimées et fichier mis à jour.")

