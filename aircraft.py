import matplotlib.pyplot as plt
import math
from airport import (IsSchengenAirport,FindAirport)

def LoadArrivals(filename):
    arrivals_list = []
    try:
        with open(filename, 'r') as arrivals_file:
            data = arrivals_file.read() #data és per llegir totes les línies del text
            Lines = data.splitlines() #Lines és per separar cada línia del text
            i=1
            while i < len(Lines): #TODO: fer que si el format està malament que se salti la línia (En teoria ja està fet perque si les parts no son 4 no fa res passa al seguent)
                parts=Lines[i].split()
                if len(parts) == 4:
                    aircraft_id = parts[0]
                    origin_airport = parts[1]
                    arrival_time = parts[2]
                    airline=parts[3]
                    if len(arrival_time) == 4: #Per si de cas perquè en els departures hi havia algunes hores que no seguien el format HH:MM
                        arrival_time = "0" + arrival_time
                    if arrival_time[-3]==":":
                        new_aircraft = Aircraft(aircraft_id, airline,origin_airport, arrival_time)
                        arrivals_list.append(new_aircraft)
                i+=1
    except FileNotFoundError:
        return []
    return arrivals_list

def LoadDepartures(filename):
    """Llegeix l'arxiu de sortides i retorna una llista d'Aircraft modificats."""
    departures_list = []
    try:
        with open(filename, 'r') as departures_file:
            data = departures_file.read()
            Lines = data.splitlines()
            i = 1
            while i < len(Lines):
                parts = Lines[i].split()
                if len(parts) >= 4:
                    aircraft_id = parts[0]
                    destination = parts[1]
                    departure_time = parts[2]
                    airline = parts[3]
                    # Creem Aircraft buidant les dades d'arribada però posant bé el format de les hores perque no hi hagi problemes
                    if len(departure_time) == 4:
                        departure_time = "0" + departure_time
                    new_aircraft = Aircraft(aircraft_id, airline)
                    new_aircraft.destination_airport = destination
                    new_aircraft.departure_time = departure_time
                    departures_list.append(new_aircraft)
                i += 1
        return departures_list, 0
    except FileNotFoundError:
        return [], -1
    except Exception as e:
        print(f"Error loading departures: {e}")
        return [], -1

class Aircraft:
    def __init__(self, aircraft_id, airline, origin_airport="", arrival_time=""):
        self.aircraft_id=aircraft_id #string
        self.airline=airline #3 characters with the ICAO code of the airline
        self.origin_airport=origin_airport #4 characters with the ICAO code of the airport the aircraft is coming from
        self.arrival_time=arrival_time #5 characters with format hh:mm
        self.destination_airport = "" # ICAO de destí
        self.departure_time = ""     # Format hh:mm

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
    plt.bar(Vxh, Vyh, color="orange", edgecolor="black")
    plt.title("Landing frequency during the day")
    plt.xlabel("Hour of the day")
    plt.ylabel("Number of aircrafts")
    plt.show()

def SaveFlights(aircrafts, filename):
    if not aircrafts:
        print("Error: The aircraft list is empty. No file created.")
        return -1
    try:
        with open(filename, "w") as f:
            f.write("AIRCRAFT ORIGIN ARRIVAL AIRLINE\n")
            i = 0
            while i < len(aircrafts):
                Line = aircrafts[i]
                id_f = Line.aircraft_id
                origin_f = Line.origin_airport
                time_f = Line.arrival_time
                airline_f = Line.airline
                if id_f=="":
                    id_f="-"
                if origin_f=="":
                    origin_f="-"
                if time_f=="":
                    time_f="-"
                if airline_f=="":
                    airline_f="-"
                f.write(f"{id_f} {origin_f} {time_f} {airline_f}\n")
                i += 1
        return 0
    except Exception as e: #Si per alguna raó no es pot escriure al fitxer o el que sigui
        print(f"Error saving file: {e}")
        return -1

def PlotAirlines (aircrafts):
    if not aircrafts:
        print("Error: The aircraft list is empty. No plot to show.")
        return -1
    AirlinesFound = [] #Aqui s'aniran posant les aerolínies que formaran l'eix X
    count=[] #Aquí quants avions de cada aerolínia hi haurà (eix Y)
    i=0
    while i<len(aircrafts): #Anem aircraft per aircraft
        airline1=aircrafts[i].airline
        Found=False
        j=0
        while j<len(AirlinesFound): #Mirem si ja ha sortit abans per afegir-lo al comptador
            if AirlinesFound[j]==airline1: #Si ja estava afegir-lo al comptador
                Found=True
                count[j]=count[j]+1
            j+=1
        if not Found: #Si no l'ha trobat afegir la nova aerolínia al comptador
            AirlinesFound.append(airline1)
            count.append(1)
        i+=1
    plt.figure(figsize=(15, 7))  # Prova per veure bé el gràfic: fa la finiestra més ampla
    plt.bar(AirlinesFound, count, color="#ffc9e1", edgecolor="black")
    plt.xticks(rotation=90, fontsize=9)  # Gira els noms en vertical perquè si no se solapen
    plt.title("Number of flights per airline")
    plt.xlabel("Airline")
    plt.ylabel("Number of flights")
    plt.tight_layout() # els eixos s'ajusten i no es talla res per sota
    plt.show()

def PlotFlightsType (aircrafts):
    if not aircrafts:
        print("Error: The aircraft list is empty. No plot to show.")
        return -1
    i=0
    schengen=0
    while i<len(aircrafts): #Comptador dels schengen
        origin1=aircrafts[i].origin_airport
        if IsSchengenAirport(origin1):
            schengen+=1
        i+=1
    non_schengen=len(aircrafts)-schengen
    plt.bar("Flights", [schengen], color="#e1c9ff", label="Schengen")
    plt.bar("Flights", [non_schengen], bottom=[schengen], color="#ccffc9", label="No Schengen")
    plt.title("Origin of Aircrafts")
    plt.ylabel("Count of Flights")
    plt.legend()
    plt.show()

def MapFlights(aircrafts, airports,filename="flights.kml"):
    LEBL = FindAirport(airports, "LEBL")
    # Si LEBL no està al file d'aeroports que marqui error
    if LEBL == -1:
        print("Error: LEBL coordinates not found in the airports list. Cannot plot trajectories.")
        return -1
    with open (filename, "w") as f:
     #  f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
        f.write('<Document>\n')
        f.write('<name>Flight Trajectories to LEBL</name>\n')
        i=0
        while i < len(aircrafts):
            airport_origin=FindAirport(airports, aircrafts[i].origin_airport)
            if airport_origin!=-1:
                if airport_origin.schengen:
                    color="ffffc9e1"
                else:
                    color="ffc9ffcc"
                f.write(f"""    
                            <Placemark>
                                <name>{aircrafts[i].aircraft_id} ({aircrafts[i].origin_airport} to LEBL)</name>
                                <Style>
                                    <LineStyle>
                                        <color>{color}</color>
                                        <width>3</width>
                                    </LineStyle>
                                </Style>
                                <LineString>
                                    <tessellate>1</tessellate>
                                    <altitudeMode>clampToGround</altitudeMode>
                                    <coordinates>
                                        {airport_origin.longitude},{airport_origin.latitude},0 {LEBL.longitude},{LEBL.latitude},0
                                    </coordinates>
                                </LineString>
                            </Placemark>
                                """)
            i += 1
        f.write("</Document>\n</kml>")
    return filename

def HaversineDistance(lat1, lon1, lat2, lon2):
    R = 6371 # Earth radius
    # Convert degrees to rad
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    # Fórmula de Haversine
    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance

def LongDistanceArrivals(aircrafts,airports): #TODO: que es vegi a la pantalla de sota
    if not aircrafts:
        print("Error: The aircraft list is empty. No plot to show.")
        return -1
    long_distance=[]
    LEBL= FindAirport(airports, "LEBL")
    # Si LEBL no està al file d'aeroports que marqui error
    if LEBL == -1:
        print("Error: LEBL coordinates not found in the airports list. Cannot plot trajectories.")
        return -1
    i=0
    while i < len(aircrafts):
        origin1 = FindAirport(airports, aircrafts[i].origin_airport)
        if origin1 != -1:
            distance=HaversineDistance(origin1.latitude, origin1.longitude, LEBL.latitude, LEBL.longitude)
            if distance>2000:
                long_distance.append(aircrafts[i])
        i+=1
    return long_distance

# test section
if __name__ == "__main__":
    import airport
    aircrafts = LoadArrivals ("Arrivals.txt")
    airports_list=airport.LoadAirports("airports.txt")
    if not aircrafts:
        print("Error: Couldn't load arrivals or empty file.")
    else:
        # 2. Prova gràfics
        print("Ploting arrivals per hour...")
        PlotArrivals(aircrafts)
        print("Ploting flights per airline...")
        PlotAirlines(aircrafts)
        print("Ploting schengen flights...")
        PlotFlightsType(aircrafts)

        # 3. Prova generació Mapa KML
        print("Generating trajectories KML file...")
        MapFlights(aircrafts, airports_list, "test_flights.kml")

        # 4. Prova detecció de llarga distància
        print("Searching long distance flights...")
        long_distance_flights = LongDistanceArrivals(aircrafts, airports_list)
        print(f"Found flights requiring inspection: {len(long_distance_flights)}")
        i = 0
        while i < len(long_distance_flights):
            print(f" - Aircraft: {long_distance_flights[i].aircraft_id} from {long_distance_flights[i].origin_airport}")
            i += 1
