import pandas as pd
import time

data_trip = pd.read_csv("./modifier data/202207-bluebikes-tripdata.csv")

def get_next_trip(last_trip_index):
    """prend l'index du trip considérer (si y avait plusieurs trip on regarde bien le dernier parmis eux)
    dans la simulation et retourne le temps en secondes du ou des prochains.
    """
    next_idx = last_trip_index + 1
    sec = int(data_trip['discret_time'][next_idx])
    dic = {next_idx: sec}
    i = next_idx + 1
    while int(data_trip['discret_time'][i]) == sec:
        dic[i] = int(data_trip['discret_time'][i])
        i += 1
    return dic

print(get_next_trip(54))
re = {0:1, 1:2, 2:4}
print(re[0])
print(list(re.keys())[2])
re[3] = 5
print(re)
for i in range(4, 10):
    re[i] = i+1
print(re)


comp = 0
a = time.time()
for _ in range(2678900):
    comp += 1
b = time.time()    
print(comp)
print(f"temps: {b - a}")



