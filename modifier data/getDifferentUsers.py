import pandas as pd

data = pd.read_csv("./modifier data/201501-hubway-tripdata.csv")

users = data[['usertype', 'birth year', 'gender']]
unique_users = users.drop_duplicates()

print(f"nombre de users potentielement différent: {len(unique_users)}")

output_path = "unique_users.csv"
unique_users.to_csv(output_path, index=False)

