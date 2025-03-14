import matplotlib.pyplot as plt


#######################################################
#####
##### distribution of accepted offers per user
#####
#######################################################

accepted_offers_per_users = {}
count_unique_user_ac_offer = 0

def new_accepted_offer(user_id):
    global count_unique_user_ac_offer
    if user_id == 2:
        return
    if user_id not in accepted_offers_per_users:
        count_unique_user_ac_offer += 1
        accepted_offers_per_users[user_id] = 0
    accepted_offers_per_users[user_id] += 1

def compute_result_accepted_offer_per_user(nb_user_total, count_zero_accepted = False):
    global count_unique_user_ac_offer
    repartition = {}
    #print(accepted_offers_per_users)
    for nb in accepted_offers_per_users.values():
        if nb not in repartition:
            repartition[nb] = 0
        repartition[nb] += 1
        
    sorted_repartition = dict(sorted(repartition.items()))
    print(sorted_repartition)
    
    if count_zero_accepted:
        #On prend aussi en compte les gens qui n'ont pas accepté d'offre
        sorted_repartition[0] = nb_user_total - count_unique_user_ac_offer
        y_raw = [(v/nb_user_total * 100) for v in sorted_repartition.values()]
    else:
       y_raw = [(v/count_unique_user_ac_offer * 100) for v in sorted_repartition.values()] 
    
    x_raw = list(sorted_repartition.keys())
    x_transformed = []
    y_transformed = []
    interval_start = 10
    
    for x, y in zip(x_raw, y_raw):
        if x < interval_start:
            x_transformed.append(str(x))
            y_transformed.append(y)
        else:
            # On regroupe par intervalles
            interval = f"{(x // 30) * 30}-{(x // 30) * 30 + 29}"
            if len(x_transformed) > 0 and x_transformed[-1] == interval:
                y_transformed[-1] += y  
            else:
                x_transformed.append(interval)
                y_transformed.append(y)
    
    positions = range(len(x_transformed))  
    plt.bar(positions, y_transformed, color='skyblue')
    plt.xlabel("Nombre d'offres acceptées")
    plt.ylabel("Pourcentage du nombre d'utilisateur")
    plt.title("Répartition des utilisateurs par nombre d'offres acceptées")
    plt.xticks(positions, x_transformed, rotation=45, ha='right')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()
    
def compute_proposed_per_considere():
    pass


#######################################################
#####
##### distribution of stats
#####
#######################################################

def show_stats(batch_stats1, batch_stats2):
    # Statistiques à comparer sur un même graphique
    common_stats = ["budget", "service_level", "percent_problematic"]
    
    # Statistiques affichées indépendamment
    independent_stats = ["proposed_1", "accepted_1", "percent_accepted_1", 
                         "proposed_2", "accepted_2", "percent_accepted_2"]

    #fig, axes = plt.subplots(len(common_stats) + len(independent_stats), 1, figsize=(10, (len(common_stats) + len(independent_stats)) * 3))
    
    batches1 = [entry["batch"] for entry in batch_stats1]
    batches2 = [entry["batch"] for entry in batch_stats2]
    
    for i, stat in enumerate(common_stats):
        plt.figure(figsize=(10, 5))
        values1 = [entry[stat] for entry in batch_stats1]
        values2 = [entry[stat] for entry in batch_stats2]
        
        plt.plot(batches1, values1, marker='o', linestyle='-', color='b', label="Algo 1")
        plt.plot(batches2, values2, marker='s', linestyle='--', color='r', label="Algo 2")
        plt.xlabel("Batch Number")
        plt.ylabel(stat.replace("_", " ").title())
        plt.title(f"Comparaison de {stat.replace('_', ' ').title()}")
        plt.grid(True)
        plt.legend()
        plt.show()

    """# Affichage indépendant pour les autres statistiques
    for j, stat in enumerate(independent_stats):
        values1 = [entry[stat] for entry in batch_stats1]
        values2 = [entry[stat] for entry in batch_stats2]
        
        ax = axes[len(common_stats) + j]
        ax.plot(batches1, values1, marker='o', linestyle='-', color='b', label=f"Algo 1 - {stat}")
        ax.plot(batches2, values2, marker='s', linestyle='--', color='r', label=f"Algo 2 - {stat}")
        ax.set_xlabel("Batch Number")
        ax.set_ylabel(stat.replace("_", " ").title())
        ax.set_title(f"Évolution de {stat.replace('_', ' ').title()} par Batch")
        ax.grid(True)
        ax.legend()"""

    

#######################################################
#####
##### EN FONCTION DU MOMENT DE LA JOURNEE
#####
#######################################################

