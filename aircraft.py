import matplotlib.pyplot as plt

def LoadArrivals(filename):
    arrivals_list = []
    try:
        with open(filename, 'r') as arrivals_file:
            data = arrivals_file.read() #data és per llegir totes les línies del text
            Lines = data.splitlines() #Lines és per separar cada línia del text
            i=1
            while i < len(Lines): #TODO: fer que si el format està malament que se salti la línia
                parts=Lines[i].split()
                if len(parts) == 4:
                    aircraft_id = parts[0]
                    origin_airport = parts[1]
                    arrival_time = parts[2]
                    airline=parts[3]
                    if arrival_time[-3]==":":
                        new_aircraft = Aircraft(aircraft_id, airline,origin_airport, arrival_time)
                        arrivals_list.append(new_aircraft)
                i+=1
    except FileNotFoundError:
        return []
    return arrivals_list

class Aircraft:
    def __init__(self, aircraft_id, airline, origin_airport,arrival_time):
        self.aircraft_id=aircraft_id #string
        self.airline=airline #3 characters with the ICAO code of the airline
        self.origin_airport=origin_airport #4 characters with the ICAO code of the airport the aircraft is coming from
        self.arrival_time=arrival_time #5 characters with format hh:mm

def PlotArrivals (aircrafts):
    if not aircrafts:
        print("Error: The aircraft list is empty. Cannot plot.")
        return
    i=0
    Vyh=[0]*24
    while i < len(aircrafts):
        try:
            # Traiem la hora de cada arrival time
            hour = int(aircrafts[i].arrival_time.split(':')[0])
            if 0 <= hour <= 23:
                Vyh[hour]=Vyh[hour]+1
        except (ValueError, IndexError):
            pass
        i+=1
    Vxh=[0]*24
    j=1
    while j < 24:
        Vxh[j]=Vxh[j]+j
        j+=1
    print("Vyh:",Vyh)
    print("Vxh:",Vxh)
    plt.bar(Vxh, Vyh, color="orange", edgecolor="black")
    plt.title("Landing frequency during the day")
    plt.xlabel("Hour of the day")
    plt.ylabel("Number of aircrafts")
    plt.show()
