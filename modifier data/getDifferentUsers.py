import pandas as pd
import numpy as np

data = pd.read_csv("./modifier data/202207-bluebikes-tripdata.csv")

users = data[["usertype","postal code"]]
unique_users = users.drop_duplicates()
unique_users['id'] = range(1, len(unique_users) + 1)

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

output_path = "./modifier data/unique_users.csv"
unique_users.to_csv(output_path, index=False)

