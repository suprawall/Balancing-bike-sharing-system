import pandas as pd
import time
from sortedcontainers import SortedDict

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

print(get_next_trip(3))
re = {0:1, 1:2, 2:4}
print(re[0])
print(list(re.keys())[2])
re[3] = 5
print(re)
for i in range(4, 10):
    re[i] = i+1
print(re)

remember_offre = {2:[(70,-59), 54], 6:[(56,2), 39]}
for idx, inf in remember_offre.items():
    print(idx)
    pos, id = inf
    print(pos)
    print(id)
    print("======")
    
for i in range(10):
    if remember_offre and i == next(iter(remember_offre)):
        print(i)
        remember_offre.pop(i)
        
Remember_offre = SortedDict()
Remember_offre[5] = 0
print(Remember_offre)
Remember_offre[1] = 1
print(Remember_offre)
Remember_offre[10] = 6
print(Remember_offre)
Remember_offre[2] = 8
print(Remember_offre)


comp = 0
a = time.time()
for _ in range(2678900):
    comp += 1
b = time.time()    
print(comp)
print(f"temps: {b - a}")



