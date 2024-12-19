from datetime import datetime, timedelta
import statistics

class Batch():
    def __init__(self):
        self.current_batch_start = None
    
    def is_nv_batch(self, starttime):
        """dans le dataset les trips sont par date chronologique donc 
        à chaque nouvelle requête on regarde si on est dans un nouveau batch ou pas
        (True ou False)

        Args:
            starttime (string): 2022-07-01 00:00:01.2710: année-moi-jour heure:minute:seconde
        """
        
        current_time = datetime.strptime(starttime.split(".")[0], "%Y-%m-%d %H:%M:%S")

        # Calculer le début du batch correspondant
        batch_start = current_time.replace(minute=0, second=0, microsecond=0)
        while batch_start.hour % 2 != 0: 
            batch_start -= timedelta(hours=1)

        # Si c'est le premier batch ou un nouveau batch
        if self.current_batch_start is None or batch_start != self.current_batch_start:
            self.current_batch_start = batch_start
            return True

        return False
    
    
def get_z(data_trip):
    """
    Calculer une fois: sur le fichier 202207-blubikes-tripdata,
    il y a en moyenne 1151 requêtes par batch.
    """
    batch = Batch()
    
    counts = []
    c = 0
    for _, row in data_trip.iterrows():
        if(batch.is_nv_batch(row['starttime'])):
            counts.append(c)
            c = 0
        else:
            c += 1
    return statistics.mean(counts)
    
"""batch = Batch()

print(batch.is_nv_batch("2022-07-01 00:00:01.2710"))  # True (premier batch)
print(batch.is_nv_batch("2022-07-01 01:59:59.0000"))  # False (même batch)
print(batch.is_nv_batch("2022-07-01 02:00:00.0000"))  # True (nouveau batch)
print(batch.is_nv_batch("2022-07-01 04:05:00.0000"))  # True
print(batch.is_nv_batch("2022-07-01 22:00:00.0000"))  # True
print(batch.is_nv_batch("2022-07-01 23:59:59.0000"))  # False
print(batch.is_nv_batch("2022-07-02 00:00:00.0000"))  # True"""

