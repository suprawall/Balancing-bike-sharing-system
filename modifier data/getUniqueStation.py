import pandas as pd

data = pd.read_csv("./modifier data/202207-bluebikes-tripdata.csv")

start_stations = data[['start station id', 'start station latitude', 'start station longitude']]
end_stations = data[['end station id', 'end station latitude', 'end station longitude']]

start_stations.columns = ['station id', 'latitude', 'longitude']
end_stations.columns = ['station id', 'latitude', 'longitude']

all_stations = pd.concat([start_stations, end_stations])
unique_stations = all_stations.drop_duplicates(subset=['station id']).reset_index(drop=True)
unique_stations = unique_stations.sort_values('station id')

print(f"nombre de station: {len(unique_stations)}")

output_path = "unique_stations.csv"
unique_stations.to_csv(output_path, index=False)