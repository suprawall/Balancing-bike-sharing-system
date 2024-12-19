

####################################################
#####
##### MEILLEUR VERSION DE IDS
#####
####################################################
def IDS(latu, longu, current_user):
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
    if default_target in C or len(C) == 0:
        print(C)
        print(f"default target: {default_target.id}")
        print(f"pas d'offre possible pour l'user numéro {current_user.id}")
        return None, None

    station_offre = find_min_station(C, latu, longu)
    prix_offre = pricing_mechanisme()

    print(f"voici l'offre pour l'user numéro {current_user}: aller à {station_offre}, pour une récompense de {prix_offre}")

    return station_offre, prix_offre
#####################################################
