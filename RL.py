import os
import random
import csv

class Environement:
    def __init__(self):
        self.bdd = "202207-bluebikes-tripdata.csv"
        self.tabbdd = ["202207-bluebikes-tripdata.csv"]
        self.bdd_folder = "modifier data"
    
    def reset(self, same=False):
        """same = True on reset sur la meme base de donnée, sinon on trouve au harsard une autre pas déja utilisée"""
        
        if same:
            chemin_fichier = os.path.join(self.bdd_folder, self.bdd)
            with open(chemin_fichier, mode="r", encoding="utf-8") as file:
                    reader = csv.DictReader(file)
                    premiere_ligne = next(reader, None)
                    return premiere_ligne
        
        fichiers_csv = [f for f in os.listdir(self.bdd_folder) if "bluebikes" in f]
        fichiers_disponibles = [f for f in fichiers_csv if f not in self.tabbdd]
        
        if not fichiers_disponibles:
            print("Tous les fichiers CSV ont déjà été utilisés.")
            return None
        
        self.bdd = random.choice(fichiers_disponibles)
        self.tabbdd.append(self.bdd)
        
        print(f"Fichier sélectionné : {self.bdd}")
        chemin_fichier = os.path.join(self.bdd_folder, self.bdd)
        with open(chemin_fichier, mode="r", encoding="utf-8") as file:
                reader = csv.reader(file)
                premiere_ligne = next(reader, None) 
                return premiere_ligne
    
    def step(self):
        pass
    
    
env = Environement()
obs = env.reset(same=True)

print(obs)

alpha = 0.1  
gamma = 0.99  
epsilon = 0.1  
episodes = 100

