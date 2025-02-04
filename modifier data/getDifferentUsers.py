import pandas as pd
import numpy as np
from itertools import count

data = pd.read_csv("./modifier data/202207-bluebikes-tripdata.csv")
data2 = pd.read_csv("./modifier data/202207-bluebikes-tripdata2.csv")
users = data[["usertype","postal code"]]


unique_users = []
id_counter = count(1)  # Générateur d'IDs uniques

grouped_users = users.groupby(['usertype', 'postal code'])

for (_, group) in grouped_users:
    sampled_group = group.iloc[:10]  # Prendre au max 10 occurrences
    sampled_group = sampled_group.copy()  # Éviter les erreurs d'assignation sur les slices
    sampled_group['id'] = [next(id_counter) for _ in range(len(sampled_group))]
    unique_users.append(sampled_group)

unique_users = pd.concat(unique_users)


print(f"nombre de users potentielement différent: {len(unique_users)}")

gamma_thresholds = [0, 250, 500, 750, 1000, 1500, 2000]
gamma_probs = [0.1, 0.35, 0.55, 0.7, 0.85, 0.95, 1.0]

cost_thresholds = [0, 0.1, 0.2, 0.5, 1.0, 1.5, 2.0]
cost_probs = [0.1, 0.3, 0.5, 0.7, 0.85, 0.95, 1.0]

def sample_from_cdf(thresholds, probs):
    r = np.random.uniform(0, 1)  
    for t, p in zip(thresholds, probs):
        if r <= p:
            return t
    return thresholds[-1]

unique_users['gamma_u'] = unique_users.apply(lambda x: sample_from_cdf(gamma_thresholds, gamma_probs), axis=1)
unique_users['c_u'] = unique_users.apply(lambda x: sample_from_cdf(cost_thresholds, cost_probs), axis=1)

print(f"nombre de personne pouvant 0m : {(unique_users['gamma_u'] == 0).sum()}")
print(f"nombre de personne pouvant 250m : {(unique_users['gamma_u'] == 250).sum()}")
print(f"nombre de personne pouvant 500m : {(unique_users['gamma_u'] == 500).sum()}")
print(f"nombre de personne pouvant 750m : {(unique_users['gamma_u'] == 750).sum()}")
print(f"nombre de personne pouvant 1000m : {(unique_users['gamma_u'] == 1000).sum()}")
print(f"nombre de personne pouvant 1500m : {(unique_users['gamma_u'] == 1500).sum()}")
print(f"nombre de personne pouvant 2000m : {(unique_users['gamma_u'] == 2000).sum()}")

trips_count = data2.groupby('user_id').size().reset_index(name='number_of_trips')

# Fusionner les données avec unique_users pour ajouter la colonne number_of_trips
unique_users = unique_users.merge(trips_count, left_on='id', right_on='user_id', how='left')

# Remplir les utilisateurs sans voyages avec 0 (au cas où il y en aurait)
unique_users['number_of_trips'].fillna(0, inplace=True)

# Sauvegarder les données
output_path = "./modifier data/unique_users2.csv"
unique_users.to_csv(output_path, index=False)

print("Fichier unique_users.csv sauvegardé avec succès.")

