import numpy as np
import pandas as pd
import random
from scipy.stats import uniform
import User
import Station
import DBPUCB

data = pd.read_csv("./modifier data/unique_stations.csv")

NB_USER = 100
NB_STATION = len(data)

def Simulation(nb_user, nb_station):
    stations = []
    for _, row in data.iterrows():  
        station_id = row['station id']
        latitude = row['latitude']
        longitude = row['longitude']
        stations.append(Station(station_id, (latitude, longitude), random.randint(0,10), 10))
    users = [User()]
    