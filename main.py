import numpy as np
import pandas as pd
import random
from scipy.stats import uniform
import User
import Station
import math
import DBPUCB

data_stations = pd.read_csv("./modifier data/unique_stations.csv")
data_trip = pd.read_csv("./modifier data/hubway-tripdata-with-user_id.csv")
data_user = pd.read_csv("./modifier data/unique_users.csv")

NB_USER = len(data_user)
NB_STATION = len(data_stations)
STATIONS = []
USERS = []

def init():
    stations = []
    for _, row in data_stations.iterrows():  
        station_id = row['station id']
        latitude = row['latitude']
        longitude = row['longitude']
        stations.append(Station(station_id, (latitude, longitude), random.randint(0,10), 10))
    users = []
    for _, row in data_user.iterrows():
        users.append(User(row['id'], row['gamma_u'], row['c_u']))
    
    return stations, users

def pricing_mechanisme():
    pass

def distance(lat1, long1, lat2, long2):
    R = 6371000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(long2 - long1)

    # Calcul de la formule de Haversine
    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Distance en mètres
    distance = R * c
    return distance

def find_min_station(stations, latu, longu):
    """retourne la station la plus proche d'un utilisateur
    """
    min_d = None
    min_station = None
    for station in stations:
        lats = station.localisation[0]
        longs = station.localisation[1]
        d = distance(latu, longu, lats, longs)
        if(d < min_d or min_d is None):
            min_d = d
            min_station = station
    return min_station
        

def Simulation(nb_user, nb_station):
    for _, row in data_trip.iterrows():
        current_id = row['user_id']
        current_user = USERS_DICT.get(current_id)
        start_lat = row['start station latitude']
        start_long = row['start station longitude']
        latu, longu = current_user.generate_random_location((start_lat, start_long), 500)
        C = STATIONS.copy()
        
        # cherche la default target
        default_target = find_min_station(STATIONS, latu, longu)
                
        #Construire liste des stations candidates
        for station in STATIONS:
            status = station.problematic()
            lats = station.localisation[0]
            longs = station.localisation[1]
            d = distance(latu, longu, lats, longs)
            if(d > current_user.max_distance):
                C.remove(station)
                continue
            if(current_user.action == "pick" and status != "empty"):
                C.remove(station)
                continue
            if(current_user.action == "return" and status != "full"):
                C.remove(station)
        
        #Vérification et offre
        if (default_target in C or len(C) == 0):
            continue
        station_offre = find_min_station(C, latu, longu)
        prix_offre = pricing_mechanisme()
        
        return station_offre, prix_offre
        
            


STATIONS, USERS = init()
USERS_DICT = {user.id: user for user in USERS}
STATIONS_DICT = {station.id: station for station in STATIONS}

    