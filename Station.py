class Station:
    def __init__(self, id, localisation, bikes, capacity):
        self.id = id
        self.localisation = localisation
        self.bikes = bikes
        self.capacity = capacity

    def is_problematic(self, action):
        if action == "pick" and self.bikes == 0:
            return True
        if action == "return" and self.bikes == self.capacity:
            return True
        return False