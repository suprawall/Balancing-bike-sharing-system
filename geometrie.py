import math

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

def midpoint(lat1, long1, lat2, long2):
    # Convertir les latitudes et longitudes en radians
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    lambda1 = math.radians(long1)
    lambda2 = math.radians(long2)
    
    # Calculer la différence de longitude
    delta_lambda = lambda2 - lambda1
    
    # Calculer le point médian
    Bx = math.cos(phi2) * math.cos(delta_lambda)
    By = math.cos(phi2) * math.sin(delta_lambda)
    phi_mid = math.atan2(math.sin(phi1) + math.sin(phi2), 
                         math.sqrt((math.cos(phi1) + Bx) ** 2 + By ** 2))
    lambda_mid = lambda1 + math.atan2(By, math.cos(phi1) + Bx)
    
    # Convertir le résultat en degrés
    lat_mid = math.degrees(phi_mid)
    long_mid = math.degrees(lambda_mid)
    
    return lat_mid, long_mid

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



"""lat1 = 42.35082680669095
long1 = -71.0898108780384

lat2 = 42.3294633
long2 = -71.0901582

lat3, long3 = midpoint(lat1, long1, lat2, long2)

print(distance(lat1, long1, lat2, long2))
print(lat3)
print(long3)
print(distance(lat1, long1, lat3, long3))"""