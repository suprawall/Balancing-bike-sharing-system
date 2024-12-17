import pandas as pd
import random

# Charger les deux fichiers CSV
df = pd.read_csv('./modifier data/201501-hubway-tripdata.csv')
unique_users = pd.read_csv('./modifier data/unique_users.csv')

# Fusionner les deux DataFrames pour ajouter la colonne 'user_id' dans df sans supprimer les doublons
df = pd.merge(df, unique_users[['usertype', 'birth year', 'gender', 'id']], 
              on=['usertype', 'birth year', 'gender'], 
              how='left')
df = df.rename(columns={'id': 'user_id'})
# Sauvegarder le fichier modifié
df.to_csv('./modifier data/hubway-tripdata-with-user_id.csv', index=False)

print("Colonne 'user_id' ajoutée et fichier sauvegardé.")

choix = random.randint(1,169)

print(f"nombre de trajet de l'user {choix} : {(df['user_id'] == choix).sum()}")


