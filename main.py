import numpy as np
import pandas as pd
import random
from scipy.stats import uniform
import User
import Station
import DBPUCB

data_stations = pd.read_csv("./modifier data/unique_stations.csv")
data_trip = pd.read_csv("./modifier data/201501-hubway-tripdata.csv")

NB_USER = 100
NB_STATION = len(data_stations)

def Simulation(nb_user, nb_station):
    stations = []
    for _, row in data_stations.iterrows():  
        station_id = row['station id']
        latitude = row['latitude']
        longitude = row['longitude']
        stations.append(Station(station_id, (latitude, longitude), random.randint(0,10), 10))
    users = [User()]
    