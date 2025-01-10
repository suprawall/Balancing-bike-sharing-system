import numpy as np
import pandas as pd
import random
import math
import copy
import ExperimentTest

from scipy.stats import uniform
from User import User
from Station import Station
from Batch import Batch, get_z
from geometrie import distance, midpoint, find_min_station
#from DBPUCB import DBP_UCB

data_stations = pd.read_csv("./modifier data/unique_stations.csv")
data_trip = pd.read_csv("./modifier data/202207-bluebikes-tripdata.csv")
data_user = pd.read_csv("./modifier data/unique_users.csv")

NB_USER = len(data_user)
NB_STATION = len(data_stations)
STATIONS = []
USERS = []
CAPACITE_STATION = 7

def init():
    stations = []
    count_full = 0
    count_empty = 0
    for _, row in data_stations.iterrows():  
        station_id = row['station id']
        latitude = row['latitude']
        longitude = row['longitude']
        bikes = random.randint(0,CAPACITE_STATION)
        stations.append(Station(station_id, (latitude, longitude), bikes, CAPACITE_STATION))
        if bikes == CAPACITE_STATION:
            count_full += 1
        elif bikes == 0:
            count_empty += 1
    print(f"il y a {count_empty} stations vide et {count_full} stations pleine sur 430 stations: {int((count_empty+count_full)/430*100)}% sont problématique")
    users = []
    for _, row in data_user.iterrows():
        users.append(User(row['id'], row['gamma_u'], row['c_u']))
    
    return stations, users

def init_price(c_min=0.5, c_max=2, k=5):
    return [round(c_min + i * (c_max - c_min) / k, 2) for i in range(k + 1)]

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


def DBP_UCB(para):
    prices, n, budget, N_n, F_n, B_n = para
    z_hn = 1151     # voir get_z dans Batch.py
    N = 2 * z_hn
    
    F_tilde = [F_n[i] + math.sqrt((2 * math.log(n+1)) / (N_n[i] + 1e-9)) for i in range(len(prices))]     # + 1e-9, pour eviter la division par 0
    
    i_n = max(
        range(len(prices)),
        key=lambda i: min(F_tilde[i], budget / (N * prices[i]))
        if prices[i] <= B_n else -float('inf')
        )
    
    return prices[i_n]
    

def IDS(latu, longu, current_user, info_for_DBP):
    
    # cherche la default target
    default_target, _ = find_min_station(STATIONS, latu, longu)
            
    #Construire liste des stations candidates
    C = [
        station for station in STATIONS
        if (
            distance(latu, longu, station.localisation[0], station.localisation[1]) <= current_user.max_distance
            and (
                (current_user.action == "pick" and station.problematic() != "full")
                or (current_user.action == "return" and station.problematic() != "empty")
            )
        )
    ]
    #print("=================================================")
    #Vérification et offre
    if (default_target in C or len(C) == 0):
        """print(C)
        print(f"default target: {default_target.id}")
        print(f"pas d'offre possible pour l'user numéro {current_user.id}")"""
        return None, None
    station_offre, distance_s = find_min_station(C, latu, longu)
    prix_offre = DBP_UCB(info_for_DBP)
    
    #print(C)
    #print(f"voici l'offre pour l'user numéro {current_user.id}: aller à station {station_offre.id} au lieu de la {default_target.id} et marcher {int(distance(latu, longu, station_offre.localisation[0], station_offre.localisation[1]))} mètres, pour une récompense de {prix_offre}")
    
    return (station_offre, distance_s), prix_offre
        

def Simulation(batch):
    
    #Initialisation pour algo...
    prices = init_price()
    n = 0
    budget = 100
    N_n = [0 for _ in range(len(prices))]
    F_n = [0 for _ in range(len(prices))]
    B_n = budget
    
    #Init pour csv...
    last_idx = 0
    Remember_offre = {}
    next_trip = {0: int(data_trip['discret_time'][0])}
    
    #Variable pour print...
    nb_accepted_offre = 0
    nb_proposed_offre = 0
    nb_batch = 0
    
    nb_ac_per_batch = 0
    nb_pr_per_batch = 0
    total_persons_last_interval = 0
    
    for i in range(2678400):
        #Proposition Mi-parcours
        if i == Remember_offre[0]:
            #DO 2eme offre
            pass
        
        #Check si on est à un moment ou y a aucun(s) trip(s)
        first_key = list(next_trip.keys())[0]
        if i < next_trip[0]:
            continue
        
        #Algo de base
        if i == next_trip[0]:
            row = data_trip.iloc[last_idx + 1]         
            #Vérification Nouveau Batch...
            #if(i % 7200 == 0 and i != 0):
            if(batch.is_nv_batch(row['starttime'])):
                nb_batch += 1
                if(nb_batch % 10 == 0):
                    persons_in_interval = i - total_persons_last_interval
                    total_persons_last_interval = i
                    print(f"Juste pour les batchs [{nb_batch}/100] ==> proposed: {nb_pr_per_batch}, accepted: {nb_ac_per_batch} // {int(nb_ac_per_batch/nb_pr_per_batch*100)}% || {persons_in_interval} personnes au total")
                    nb_ac_per_batch = 0
                    nb_pr_per_batch = 0
                if(nb_batch == 100):
                    return nb_accepted_offre, nb_proposed_offre, nb_batch, i
                B_n += 100
                budget = B_n
                
                
            info_for_DBP = [prices, n, budget, N_n, F_n, B_n]
            
            #Get l'user
            current_id = row['user_id']
            current_user = USERS_DICT.get(current_id)
            start_lat = row['start station latitude']
            start_long = row['start station longitude']
            latu, longu = current_user.generate_random_location((start_lat, start_long), 100)
            
            #Incentives Deployment Schema
            s_star, p_star = IDS(latu, longu, current_user, info_for_DBP)
            
            if(p_star is not None):
                nb_proposed_offre += 1
                nb_pr_per_batch += 1
                i_n = prices.index(p_star)
                
                #Offre et update des variables
                y_n = current_user.accept_offer(s_star[1], p_star)
                B_n -= p_star*y_n
                F_n[i_n] = F_n[i_n] + (y_n - F_n[i_n]) / (N_n[i_n] + 1)
                N_n[i_n] += 1
                n += 1
                
                if(y_n == 1):
                    nb_accepted_offre += 1
                    nb_ac_per_batch += 1
                    ExperimentTest.new_accepted_offer(current_id)
                    tps_moitie = i + (row['discret_time'])
                    Remember_offre[tps_moitie] = [current_id, s_star[0], ]
                    #print(f"la station {s_star[0].id} a donc {s_star[0].bikes} vélos dans son stock avant la MAJ")
                    if(current_user.action == "pick"):
                        #print(f"cet utilisateur accepte l'offre, il va {current_user.action} un vélo, la station {s_star[0].id} a donc maintenant {s_star[0].bikes - 1} vélos dans son stock")
                        current_user.action = "return"
                        s_star[0].bikes -= 1
                    else:
                        #print(f"cet utilisateur accepte l'offre, il va {current_user.action} un vélo, la station {s_star[0].id} a donc maintenant {s_star[0].bikes + 1} vélos dans son stock")
                        current_user.action = "pick"
                        s_star[0].bikes += 1
        

STATIONS, USERS = init()
USERS_DICT = {user.id: user for user in USERS}
#STATIONS_DICT = {station.id: station for station in STATIONS}

batch = Batch()
nb_a, nb_p, nb_b, i = Simulation(batch)
print(f"Il y a eu {nb_a} offres acceptées sur {nb_p} proposées dans les {nb_b} premiers batch, ({int(nb_a / nb_p  * 100)}%)")
print(f"{i} itérations")
ExperimentTest.compute_result_accepted_offer_per_user(len(USERS), False)
#print(get_z(data_trip))
    