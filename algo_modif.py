import numpy as np
import pandas as pd
import random
import math
import copy

from scipy.stats import uniform
from sortedcontainers import SortedDict
from User import User
from Station import Station
from Batch import Batch, get_z
from geometrie import distance, midpoint, find_min_station
from ExperimentTest import new_accepted_offer, compute_result_accepted_offer_per_user
#from DBPUCB import DBP_UCB

data_stations = pd.read_csv("./modifier data/unique_stations.csv")
data_trip = pd.read_csv("./modifier data/202207-bluebikes-tripdata2.csv")
data_user = pd.read_csv("./modifier data/unique_users2.csv")

NB_USER = len(data_user)


def init_price(c_min=0.5, c_max=2, k=5):
    return [round(c_min + i * (c_max - c_min) / k, 2) for i in range(k + 1)]

def get_next_trip(last_trip_index):
    """prend l'index du trip considérer (si y avait plusieurs trip on regarde bien le dernier parmis eux)
    dans la simulation et retourne le temps en secondes du ou des prochains (int) et un tableau contenant les 
    index du ou des prochains trip de la base de donnée.
    """
    next_idx = last_trip_index + 1
    sec = int(data_trip['discret_time'][next_idx])
    tab =[next_idx]
    i = next_idx + 1
    while int(data_trip['discret_time'][i]) == sec:
        tab.append(i)
        i += 1
    return sec, tab


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
    

def IDS_modif(latu, longu, current_user, info_for_DBP, stations, obj_station=None):
    
    # cherche la default target
    if(obj_station is None):
        default_target, _ = find_min_station(stations, latu, longu)
    else:
        default_target = obj_station
        
            
    #Construire liste des stations candidates
    C = [
        station for station in stations
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
        

def Simulation_modif(batch, stations, user_dict):
    
    #Initialisation pour algo...
    nb_stations = len(stations)
    prices = init_price()
    print(prices)
    n = 0
    budget = 100
    N_n = [0 for _ in range(len(prices))]
    F_n = [0 for _ in range(len(prices))]
    B_n = budget
    
    #Init pour csv...
    current_idx = 0
    Remember_offre = SortedDict()           #Basé sur une structure d'arbre, ajout d'élement garde l'odre trié des clefs en O(log(n))
    idx_next_trip = [0]
    tps_next_trip = int(data_trip['discret_time'][current_idx])
    
    #Variable pour print...
    nb_accepted_offre = 0
    nb_proposed_offre = 0
    nb_accepted_offre2 = 0
    nb_proposed_offre2 = 0
    nb_batch = 0
    potential_customer = 0
    no_service_event = 0
    
    nb_ac_per_batch = 0
    nb_pr_per_batch = 0
    nb_ac_per_batch2 = 0
    nb_pr_per_batch2 = 0
    nb_considerer2 = 0
    total_persons_last_interval = 0
    
    #Var arrêt...
    arret = 2678400
    
    # Stockage des statistiques par batch
    batch_stats = []
    
    for i in range(2678400):
        if nb_batch > 370:
            return nb_accepted_offre, nb_proposed_offre, nb_accepted_offre2, nb_proposed_offre2, nb_batch, current_idx, i, batch_stats
        #Proposition Mi-parcours
        if Remember_offre and i == next(iter(Remember_offre)):
            #DO 2eme offre
            compt = 0
            for idx, info in Remember_offre.items():
                if i == idx:
                    nb_considerer2 += 1
                    compt += 1
                    user, pos, station = info
                    info_for_DBP = [prices, n, budget, N_n, F_n, B_n]
                    changement_station = False

                    s_star, p_star = IDS_modif(pos[0], pos[1], user, info_for_DBP, stations, obj_station=station)
                    if(p_star is not None):
                        nb_proposed_offre2 += 1
                        nb_pr_per_batch2 += 1
                        #Update var...
                        i_n = prices.index(p_star)
                
                        #Offre et update des variables
                        y_n = user.accept_offer(s_star[1], p_star)
                        B_n -= p_star*y_n
                        F_n[i_n] = F_n[i_n] + (y_n - F_n[i_n]) / (N_n[i_n] + 1)
                        N_n[i_n] += 1
                        n += 1
                        if(y_n == 1):
                            changement_station = True
                            nb_accepted_offre2 += 1
                            nb_ac_per_batch2 += 1
                            #Update sur la nouvelle station...
                            if(user.action == "pick"):
                                #print(f"cet utilisateur accepte l'offre, il va {current_user.action} un vélo, la station {s_star[0].id} a donc maintenant {s_star[0].bikes - 1} vélos dans son stock")
                                user.action = "return"
                                s_star[0].bikes -= 1
                            else:
                                #print(f"cet utilisateur accepte l'offre, il va {current_user.action} un vélo, la station {s_star[0].id} a donc maintenant {s_star[0].bikes + 1} vélos dans son stock")
                                user.action = "pick"
                                s_star[0].bikes += 1
                                
                    if(not changement_station):
                        #Update sur l'ancienne station...
                        if(user.action == "pick"):
                            #print(f"cet utilisateur accepte l'offre, il va {current_user.action} un vélo, la station {s_star[0].id} a donc maintenant {s_star[0].bikes - 1} vélos dans son stock")
                            user.action = "return"
                            station.bikes -= 1
                        else:
                            #print(f"cet utilisateur accepte l'offre, il va {current_user.action} un vélo, la station {s_star[0].id} a donc maintenant {s_star[0].bikes + 1} vélos dans son stock")
                            user.action = "pick"
                            station.bikes += 1
                else:
                    break
                
            for _ in range(compt):
                if Remember_offre:
                    del Remember_offre[next(iter(Remember_offre))]
        
        #Check nv batch
        if(i % 7200 == 0):
            nb_batch += 1
            if(nb_batch % 10 == 0):
                persons_in_interval = current_idx - total_persons_last_interval
                total_persons_last_interval = current_idx
                service_level = (potential_customer - no_service_event) / potential_customer if potential_customer > 0 else 0
                percent_problematic = int(sum(1 for station in stations if station.problematic() != "null") * 100 / nb_stations)
                
                batch_stats.append({
                    "batch": nb_batch,
                    "service_level": service_level,
                    "proposed_1": nb_pr_per_batch,
                    "accepted_1": nb_ac_per_batch,
                    "percent_accepted_1": int(nb_ac_per_batch / nb_pr_per_batch * 100) if nb_pr_per_batch > 0 else 0,
                    "proposed_2": nb_pr_per_batch2,
                    "accepted_2": nb_ac_per_batch2,
                    "percent_accepted_2": int(nb_ac_per_batch2 / nb_pr_per_batch2 * 100) if nb_pr_per_batch2 > 0 else 0,
                    "budget": int(B_n),
                    "percent_problematic": percent_problematic
                })
                
                print("----------------------------------------------------------------------------------------------------------------------------")
                print(f"Batch [{nb_batch - 10} --> {nb_batch}]: Service Level: {service_level}, Budget: {int(B_n)}, Stations problématiques: {percent_problematic}%")
                print(f"1ère Instance - Proposés: {nb_pr_per_batch}, Acceptés: {nb_ac_per_batch} ({batch_stats[-1]['percent_accepted_1']}%)")
                print(f"2ème Instance - Considérés: {nb_considerer2}, Proposés: {nb_pr_per_batch2}, Acceptés: {nb_ac_per_batch2} ({batch_stats[-1]['percent_accepted_2']}%)")
                
                nb_ac_per_batch = 0
                nb_pr_per_batch = 0
                nb_ac_per_batch2 = 0
                nb_pr_per_batch2 = 0
                nb_considerer2 = 0
            B_n += 50
            budget = B_n
        
        #Check si on est à un moment ou y a aucun(s) trip(s)
        if i < tps_next_trip:
            continue

        #Algo de base
        if i == tps_next_trip:
            for index in idx_next_trip:
                potential_customer += 1
                row = data_trip.iloc[index]         
                info_for_DBP = [prices, n, budget, N_n, F_n, B_n]
                
                #Get l'user
                current_id = row['user_id']
                current_user = user_dict.get(current_id)
                start_lat = row['start station latitude']
                start_long = row['start station longitude']
                latu, longu = current_user.generate_random_location((start_lat, start_long), 100)
                
                #Incentives Deployment Schema
                s_star, p_star = IDS_modif(latu, longu, current_user, info_for_DBP, stations)
                
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
                        new_accepted_offer(current_id)
                        lat_obj, long_obj = s_star[0].localisation
                        pos_moitie = midpoint(latu, longu, lat_obj, long_obj)       # Milieux entre sa position actuelle et la station ou il a accepté d'aller
                        tps_moitie = i + (row['discret_time'])
                        Remember_offre[tps_moitie] = [current_user, pos_moitie, s_star[0]]
                else:
                    if((current_user.action == "pick" and s_star.problematic() == "empty") or (current_user.action == "return" and s_star.problematic() == "full")):
                        no_service_event += 1
                        
            
            current_idx = idx_next_trip[-1] + 1                
            tps_next_trip, idx_next_trip = get_next_trip(current_idx)
    
    return nb_accepted_offre, nb_proposed_offre, nb_accepted_offre2, nb_proposed_offre2, nb_batch, current_idx, i, batch_stats
        
def execute_nv_algo(stations, users_dict):
    NB_STAION = len(stations)
    #STATIONS_DICT = {station.id: station for station in STATIONS}

    batch = Batch()
    nb_a, nb_p, nb_a2, nb_p2, nb_b, idx, i, batch_stats = Simulation_modif(batch, stations, users_dict)
    print(f"Il y a eu {nb_a} offres acceptées sur {nb_p} proposées dans les {nb_b} premiers batch, ({int(nb_a / nb_p  * 100)}%) | En première instance")
    print(f"Il y a eu {nb_a2} offres acceptées sur {nb_p2} proposées dans les {nb_b} premiers batch, ({int(nb_a2 / nb_p2  * 100)}%) | En deuxième instance")
    #compute_result_accepted_offer_per_user(len(users_dict), False)
    #print(get_z(data_trip))
    
    return nb_a, nb_p, nb_a2, nb_p2, nb_b, idx, i, batch_stats
    