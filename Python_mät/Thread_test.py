import threading
import time
import numpy as np


### Tråd som fyller matris med mätdata från radarn.
### Returnerar matrisen med rimliga tidsintervall.
class Radar (threading.Thread):

    def __init__(self):
        self.sequences = 5
        self.num_points = 2
        self.matrix = np.zeros((self.sequences, self.num_points), dtype=np.csingle) # matris som kan fyllas med mätdata
        self.lock = threading.RLock()   # Det här är tydligen bra för något. Bör kollas upp...
        super(Radar, self).__init__()


    #sequences = 5
    #num_points = 2
    #matrix = np.zeros((sequences, num_points), dtype=np.csingle) # matris som kan fyllas med mätdata

    def run(self):
        with self.lock:
            self.fill_matrix()

    def fill_matrix(self):
        k = 1
        while k < 2:        # Anger hur länge man ska mäta. Tänker att det ska vara en oändlig loop med en avbrottsfunktion sen.
            with self.lock:
                for i in range(0, self.sequences):          # Loopar igenom matrisen.
                    rand_array = np.random.rand(self.num_points)    # skapa array med random tal.
                    self.matrix[i][:] = rand_array[:]               # Fyll matrisen
                    print("Radar: \n", self.matrix)
                    time.sleep(2)                                   # Vänta
                k += 1     



### Filtrerar matrisen från Radar-klassen. 
### Returnerar en filtrerad matris.
class Filter (threading.Thread):

    def __init__(self, matrix):
        #threading.Thread.__init__(self)
        self.matrix = matrix
        self.go = 0
        self.lock = threading.RLock()   # Det här är tydligen bra för något. Bör kollas upp...
        super(Filter, self).__init__()

    def run(self):
        with self.lock:
            self.matris_funk()  # Att köra härifrån är egentligen inte optimalt om man vill kunna ändra matrisen.

    def set_matrix(self,matrix):
            self.matrix = 1*matrix
            self.go = 1

    def matris_funk(self):  # kan ta in ett argument matrix också.
    #def matris_funk(self,matrix):  # kan ta in ett argument matrix också.
        #self.matrix = matrix 
        for k in range(0,20):
            with self.lock:
                if self.go == 1:
                    print("start")
                    for i in range(0, 5):
                        self.matrix[i][0] = 2
                        print("Filter: \n", self.matrix)
                        time.sleep(2)  # vänta
                    self.go = 0
                time.sleep(1)
        
            
            

        ### Gamla koden som skriver ut vilken tråd det är som börjar och slutar    
        #print("{} started!".format(self.getName()))              # "Thread-x started!"
        #time.sleep(2.9)                                      # Pretend to work for a second
        #print("{} finished!".format(self.getName()))             # "Thread-x finished!"


def main():

    # Initiera två trådar
    radar = Radar()

    filter_matris = np.ones((5,10)) #Test-input-matris
    filter = Filter(filter_matris)

    # Nedan printas den lokala variabeln i Filter och matrisen i Radar. 
    # Och båda trådarna startas
    print(radar.matrix)
    print(filter.matrix)

    radar.start()
    filter.start()

    #time.sleep(4)

    #matris = np.zeros((5,10))
    matris = radar.matrix
    filter.set_matrix(matris)
       
    #for i in range(0, radar.sequences):
       # print(radar.matrix)
        #print(filter.matrix)
        #time.sleep(3.1)


    # Här startas filter igen men med en annan matris
    #filter_matris = np.zeros((5,10)) #Test-input-matris
    #filter = Filter(filter_matris)
    #filter.start()
    
    #for i in range(0, radar.sequences):
    #    print(filter.matrix)
    #    time.sleep(3.1)


    ### Gamla loopen som startar en massa trådar.
    #for x in range(4):                                     # Four times...
    #    filterklass = Filter(name="Filter-{}".format(x + 1))  # ...Instantiate a thread and pass a unique ID to it
    #    filterklass.start()                                   # ...Start the thread
    #    radar = Radar(name="Radar-{}".format(x + 1))  # ...Instantiate a thread and pass a unique ID to it
    #    radar.start()                                   # ...Start the thread

    #    time.sleep(2)                                     # ...Wait 0.9 seconds before starting another


if __name__ == "__main__":
    main()
