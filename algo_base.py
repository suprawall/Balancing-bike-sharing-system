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
from algo_modif import execute_nv_algo
from ExperimentTest import new_accepted_offer, compute_result_accepted_offer_per_user, show_stats
#from DBPUCB import DBP_UCB

data_stations = pd.read_csv("./modifier data/unique_stations.csv")
data_trip = pd.read_csv("./modifier data/202207-bluebikes-tripdata2.csv")
data_user = pd.read_csv("./modifier data/unique_users2.csv")

NB_USER = len(data_user)
NB_STATION = len(data_stations)
STATIONS = []
USERS = []
CAPACITE_STATION = 5

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
    return min_station, min_d

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
        return default_target, None
    station_offre, distance_s = find_min_station(C, latu, longu)
    prix_offre = DBP_UCB(info_for_DBP)
    
    #print(C)
    #print(f"voici l'offre pour l'user numéro {current_user.id}: aller à station {station_offre.id} au lieu de la {default_target.id} et marcher {int(distance(latu, longu, station_offre.localisation[0], station_offre.localisation[1]))} mètres, pour une récompense de {prix_offre}")
    
    return (station_offre, distance_s), prix_offre
        

def Simulation(batch):
    
    #Initialisation...
    prices = init_price()
    n = 0
    budget = 100
    N_n = [0 for _ in range(len(prices))]
    F_n = [0 for _ in range(len(prices))]
    B_n = budget
    
    #Variable pour print...
    nb_accepted_offre = 0
    nb_proposed_offre = 0
    nb_batch = 0
    potential_customer = 0
    no_service_event = 0
    
    nb_ac_per_batch = 0
    nb_pr_per_batch = 0
    total_persons_last_interval = 0
    
    # Stockage des statistiques par batch
    batch_stats = []
    
    for i, (_, row) in enumerate(data_trip.iterrows()):
        """if nb_batch > 30:
            return nb_accepted_offre, nb_proposed_offre, nb_batch, i, batch_stats"""
        
        potential_customer += 1      
        #Vérification Nouveau Batch...
        if(batch.is_nv_batch(row['starttime'])):
            nb_batch += 1
            if(nb_batch % 10 == 0):
                persons_in_interval = i - total_persons_last_interval
                total_persons_last_interval = i
                service_level = (potential_customer - no_service_event) / potential_customer
                percent_problematic = int(sum(1 for station in STATIONS if station.problematic() != "null") * 100 / NB_STATION)
                
                batch_stats.append({
                    "batch": nb_batch,
                    "service_level": service_level,
                    "proposed_1": nb_pr_per_batch,
                    "accepted_1": nb_ac_per_batch,
                    "percent_accepted_1": int(nb_ac_per_batch / nb_pr_per_batch * 100) if nb_pr_per_batch > 0 else 0,
                    "budget": int(B_n),
                    "percent_problematic": percent_problematic
                })
                
                print("----------------------------------------------------------------------------------------------------------------------------")
                print(f"Batch [{nb_batch - 10} --> {nb_batch}]: Service Level: {service_level}, Budget: {int(B_n)}, Stations problématiques: {percent_problematic}%")
                print(f"Proposés: {nb_pr_per_batch}, Acceptés: {nb_ac_per_batch} ({int(nb_ac_per_batch/nb_pr_per_batch*100)})%")
                """count_pb = 0
                for station in STATIONS:
                    if station.problematic() != "null":
                      count_pb += 1
                print(f"{int(count_pb*100 / NB_STATION)}% des stations sont problématiques")"""
                nb_ac_per_batch = 0
                nb_pr_per_batch = 0
            if(nb_batch == 100):
                #return nb_accepted_offre, nb_proposed_offre, nb_batch, i
                pass
            B_n += 50
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
                #print(f"la station {s_star[0].id} a donc {s_star[0].bikes} vélos dans son stock avant la MAJ")
                if(current_user.action == "pick"):
                    #print(f"cet utilisateur accepte l'offre, il va {current_user.action} un vélo, la station {s_star[0].id} a donc maintenant {s_star[0].bikes - 1} vélos dans son stock")
                    current_user.action = "return"
                    s_star[0].bikes -= 1
                else:
                    #print(f"cet utilisateur accepte l'offre, il va {current_user.action} un vélo, la station {s_star[0].id} a donc maintenant {s_star[0].bikes + 1} vélos dans son stock")
                    current_user.action = "pick"
                    s_star[0].bikes += 1
        else:
            if((current_user.action == "pick" and s_star.problematic() == "empty") or (current_user.action == "return" and s_star.problematic() == "full")):
                no_service_event += 1
                
    return nb_accepted_offre, nb_proposed_offre, nb_batch, i, batch_stats
        
                
        

STATIONS, USERS = init()
USERS_DICT = {user.id: user for user in USERS}
station_copy = copy.deepcopy(STATIONS)
users_dict_copy = copy.deepcopy(USERS_DICT)
NB_STATION = len(STATIONS)
#STATIONS_DICT = {station.id: station for station in STATIONS}

batch = Batch()
nb_a, nb_p, nb_b, i, batch_stats_1 = Simulation(batch)
print(f"Il y a eu {nb_a} offres acceptées sur {nb_p} proposées dans les {nb_b} premiers batch, ({int(nb_a / nb_p  * 100)}%)")
print(f"{i} itérations")
#ExperimentTest.compute_result_accepted_offer_per_user(len(USERS), False)
#print(get_z(data_trip))

print("=========================================================================")
print("=======================   Démarrage Nouveau Algo  =======================")
print("=========================================================================")

count_full = sum(1 for s in station_copy if s.bikes == s.capacity)
count_empty = sum(1 for s in station_copy if s.bikes == 0)

print(f"(Vérification) il y a {count_empty} stations vides et {count_full} stations pleines sur {len(station_copy)} stations: => {int((count_empty + count_full) / len(station_copy) * 100)}% sont problématiques")

nb_a_2, nb_p_2, nb_a2_2, nb_p2_2, nb_b_2, idx_2, i_2, batch_stats_2 = execute_nv_algo(station_copy, users_dict_copy)

show_stats(batch_stats_1, batch_stats_2)
