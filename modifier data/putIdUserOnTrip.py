import pandas as pd
import random
from collections import defaultdict
from itertools import cycle

# Charger les fichiers CSV
df = pd.read_csv("./modifier data/202207-bluebikes-tripdata.csv")
unique_users = pd.read_csv("./modifier data/unique_users2.csv")

# Supprimer l'ancienne colonne 'user_id' si elle existe
if 'user_id' in df.columns:
    df = df.drop(columns=['user_id'])

# Création d'un dictionnaire {(usertype, postal code): cycle([id1, id2, ..., id10])}
id_mapping = defaultdict(list)

for (key, group) in unique_users.groupby(['usertype', 'postal code']):
    id_mapping[key] = cycle(group['id'].tolist())  # Crée un itérateur cyclique

# Fonction pour assigner les IDs de manière séquentielle
def assign_new_user_id(row):
    key = (row['usertype'], row['postal code'])
    return next(id_mapping[key]) if key in id_mapping else None  # Prend le prochain ID cycliquement

# Appliquer la fonction pour réattribuer les IDs de façon équilibrée
df['user_id'] = df.apply(assign_new_user_id, axis=1)

# Sauvegarder le fichier mis à jour
df.to_csv("./modifier data/202207-bluebikes-tripdata2.csv", index=False)

print("Colonne 'user_id' mise à jour et fichier sauvegardé.")

# Vérification
print(f"Nombre d'users uniques dans trips : {df['user_id'].nunique()}")


# Vérifier un utilisateur au hasard
choix = random.randint(1, 49095)
print(f"Nombre de trajets de l'user {choix} : {(df['user_id'] == choix).sum()}")



