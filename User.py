import random

class User:
    def __init__(self, id, max_distance, cost):
        self.id = id
        self.max_distance = max_distance  # γ_u
        self.cost = cost  # c_u
        if random.uniform(0,1) < 0.5:
            self.action = "pick"
        else:
            self.action = "return"
    
    def generate_random_location(center, radius):
        lat, lon = center
        radius_in_degrees = radius / 111000  # Conversion du rayon en degrés
        rand_lat = lat + random.uniform(-radius_in_degrees, radius_in_degrees)
        rand_lon = lon + random.uniform(-radius_in_degrees, radius_in_degrees)
        return rand_lat, rand_lon

    def accept_offer(self, distance, price):
        if distance <= self.max_distance and price >= self.cost:
            return True
        return False
    
    def change_action(self):
        if self.action == "pick":
            self.action = "return"
        else:
            self.action = "pick"