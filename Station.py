class Station:
    def __init__(self, id, localisation, bikes, capacity):
        """Sattion

        Args:
            id (int): id de la station
            localisation ((x,y)): couple (latitude, longitude)
            bikes (int): nombre de vélo dans la station
            capacity (int): capacité max en vélo
        """
        self.id = id
        self.localisation = localisation
        self.bikes = bikes
        self.capacity = capacity

    def problematic(self):
        if self.bikes == 0:
            return "empty"
        if self.bikes == self.capacity:
            return "full"
        return "null"