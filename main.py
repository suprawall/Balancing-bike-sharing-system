import numpy as np
import pandas as pd
import random
from scipy.stats import uniform
from User import User
from Station import Station
import math
import DBPUCB
import copy

data_stations = pd.read_csv("./modifier data/unique_stations.csv")
data_trip = pd.read_csv("./modifier data/202207-bluebikes-tripdata.csv")
data_user = pd.read_csv("./modifier data/unique_users.csv")

NB_USER = len(data_user)
NB_STATION = len(data_stations)
STATIONS = []
USERS = []

def init():
    stations = []
    count_full = 0
    count_empty = 0
    for _, row in data_stations.iterrows():  
        station_id = row['station id']
        latitude = row['latitude']
        longitude = row['longitude']
        bikes = random.randint(0,4)
        stations.append(Station(station_id, (latitude, longitude), bikes, 4))
        if bikes == 10:
            count_full += 1
        elif bikes == 0:
            count_empty += 1
    print(f"il y a {count_empty} stations vide et {count_full} stations pleine sur 430 stations: {int((count_empty+count_full)/430*100)}% sont problématique")
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
        if(min_d is None or d < min_d ):
            min_d = d
            min_station = station
    return min_station

def IDS(latu, longu, current_user):
    
    # cherche la default target
    default_target = find_min_station(STATIONS, latu, longu)
            
    #Construire liste des stations candidates
    C = [
        station for station in STATIONS
        if (
            distance(latu, longu, station.localisation[0], station.localisation[1]) <= current_user.max_distance
            and (
                (current_user.action == "pick" and station.problematic() == "empty")
                or (current_user.action == "return" and station.problematic() == "full")
            )
        )
    ]
    print("=================================================")
    #Vérification et offre
    if (default_target in C or len(C) == 0):
        print(C)
        print(f"default target: {default_target.id}")
        print(f"pas d'offre possible pour l'user numéro {current_user.id}")
        return None, None
    station_offre = find_min_station(C, latu, longu)
    prix_offre = pricing_mechanisme()
    
    print(C)
    print(f"voici l'offre pour l'user numéro {current_user.id}: aller à station {station_offre.id} au lieu de la {default_target.id} et marcher {int(distance(latu, longu, station_offre.localisation[0], station_offre.localisation[1]))} mètres, pour une récompense de {prix_offre}")
    
    return station_offre, prix_offre
        

def Simulation():
    for i, (_, row) in enumerate(data_trip.iterrows()):
        if(i > 4):
            return
        #Get l'user
        current_id = row['user_id']
        current_user = USERS_DICT.get(current_id)
        start_lat = row['start station latitude']
        start_long = row['start station longitude']
        latu, longu = current_user.generate_random_location((start_lat, start_long), 500)
        
        #Incentives Deployment Schema
        s_star, p_star = IDS(latu, longu, current_user)
        
        

STATIONS, USERS = init()
USERS_DICT = {user.id: user for user in USERS}
STATIONS_DICT = {station.id: station for station in STATIONS}


Simulation()
    