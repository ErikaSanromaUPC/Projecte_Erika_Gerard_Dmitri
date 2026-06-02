import matplotlib.pyplot as plt
import math
from airport import (IsSchengenAirport, FindAirport)
import os

def LoadArrivals(filename):
    arrivals_list = []
    if not os.path.exists(filename):
        return arrivals_list
    try:
        with open(filename, 'r') as arrivals_file:
            data = arrivals_file.read() #data és per llegir totes les línies del text
            Lines = data.splitlines() #Lines és per separar cada línia del text
            total_lines = 0 #Comprovacions (en el departures.txt hi havia una línia amb mal format)
            valid_lines = 0
            invalid_lines = 0
            i = 1
            while i < len(Lines):
                total_lines += 1
                line = Lines[i].strip()
                parts = line.split()

                es_valida = True
                motivo_error = ""

                # Validació columnes
                if len(parts) != 4:
                    es_valida = False
                    motivo_error = "invalid number of columns"

                if es_valida:
                    aircraft_id = parts[0]
                    origin_airport = parts[1]
                    arrival_time = parts[2]
                    airline = parts[3]

                    if len(arrival_time) == 4:
                        arrival_time = "0" + arrival_time

                    # Validació de camps
                    if aircraft_id == "":
                        es_valida = False
                        motivo_error = "empty AIRCRAFT"
                    elif len(origin_airport) != 4 or not origin_airport.isalpha():
                        es_valida = False
                        motivo_error = f"invalid ORIGIN '{origin_airport}'"
                    elif len(airline) != 3 or not airline.isalpha():
                        es_valida = False
                        motivo_error = f"invalid AIRLINE '{airline}'"
                    elif len(arrival_time) != 5 or arrival_time[2] != ":":
                        es_valida = False
                        motivo_error = f"invalid time format '{arrival_time}'"
                    else:
                        # Validació de números de l'hora de forma segura
                        try:
                            arr_hour = int(arrival_time[0:2])
                            arr_min = int(arrival_time[3:5])

                            if arr_hour < 0 or arr_hour > 23 or arr_min < 0 or arr_min > 59:
                                es_valida = False
                                motivo_error = f"time out of range '{arrival_time}'"
                        except Exception:
                            es_valida = False
                            motivo_error = f"non-numeric time '{arrival_time}'"

                if es_valida:
                    new_aircraft = Aircraft(aircraft_id, airline, origin_airport, arrival_time)
                    arrivals_list.append(new_aircraft)
                    valid_lines += 1
                else:
                    invalid_lines += 1
                    print(f"[ARRIVALS] Line {i+1} discarded: {motivo_error} -> '{Lines[i]}'")

                i += 1
        print(f"[ARRIVALS] Load summary: read={total_lines}, valid={valid_lines}, invalid={invalid_lines}")
    except FileNotFoundError:
        return []
    except Exception as e:
        print(f"[ARRIVALS] Unexpected error loading file: {e}")
        return []
    return arrivals_list

def LoadDepartures(filename):
    """Llegeix l'arxiu de sortides i retorna una llista d'Aircraft modificats."""
    departures_list = []
    try:
        with open(filename, 'r') as departures_file:
            data = departures_file.read()
            Lines = data.splitlines()
            total_lines = 0
            valid_lines = 0
            invalid_lines = 0
            i = 1

            while i < len(Lines):
                total_lines += 1
                line = Lines[i].strip()
                parts = line.split()

                es_valida = True
                motivo_error = ""

                # 1. Validació columnes
                if len(parts) != 4:
                    es_valida = False
                    motivo_error = f"invalid number of columns"

                if es_valida:
                    aircraft_id = parts[0]
                    destination = parts[1]
                    departure_time = parts[2]
                    airline = parts[3]

                    if len(departure_time) == 4:
                        departure_time = "0" + departure_time

                    # 2. Validació de camps
                    if aircraft_id == "":
                        es_valida = False
                        motivo_error = "empty AIRCRAFT"
                    elif len(destination) != 4 or not destination.isalpha():
                        es_valida = False
                        motivo_error = f"invalid DESTINATION '{destination}'"
                    elif len(airline) != 3 or not airline.isalpha():
                        es_valida = False
                        motivo_error = f"invalid AIRLINE '{airline}'"
                    elif len(departure_time) != 5 or departure_time[2] != ":":
                        es_valida = False
                        motivo_error = f"invalid time format '{departure_time}'"
                    else:
                        # 3. Validació de números de l'hora de forma segura
                        try:
                            dep_hour = int(departure_time[0:2])
                            dep_min = int(departure_time[3:5])

                            if dep_hour < 0 or dep_hour > 23 or dep_min < 0 or dep_min > 59:
                                es_valida = False
                                motivo_error = f"time out of range '{departure_time}'"
                        except Exception:
                            es_valida = False
                            motivo_error = f"non-numeric time '{departure_time}'"

                # Processem el resultat de la línia al final
                if es_valida:
                    new_aircraft = Aircraft(aircraft_id, airline)
                    new_aircraft.destination_airport = destination
                    new_aircraft.departure_time = departure_time
                    departures_list.append(new_aircraft)
                    valid_lines += 1
                else:
                    invalid_lines += 1
                    print(f"[DEPARTURES] Line {i+1} discarded: {motivo_error} -> '{Lines[i]}'")
                i += 1

        print(f"[DEPARTURES] Load summary: read={total_lines}, valid={valid_lines}, invalid={invalid_lines}")
        return departures_list, 0, total_lines, valid_lines, invalid_lines
    except FileNotFoundError:
        return [], -1, 0, 0, 0
    except Exception as e:
        print(f"[DEPARTURES] Unexpected error loading file: {e}")
        return [], -1, 0, 0, 0

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

def MapFlights(aircrafts, airports,filename="flights.kml"):
    LEBL = FindAirport(airports, "LEBL")
    # Si LEBL no està al file d'aeroports que marqui error
    if LEBL == -1:
        print("Error: LEBL coordinates not found in the airports list. Cannot plot trajectories.")
        return -1
    with open (filename, "w") as f:
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


def MapDepartures(aircrafts, airports, filename="departures.kml"):
    LEBL = FindAirport(airports, "LEBL")
    # Si LEBL no està al file d'aeroports que marqui error
    if LEBL == -1:
        print("Error: LEBL coordinates not found in the airports list. Cannot plot trajectories.")
        return -1
    with open(filename, "w") as f:
        f.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
        f.write('<Document>\n')
        f.write('<name>Departure Trajectories from LEBL</name>\n')
        i = 0
        while i < len(aircrafts):
            airport_destination = FindAirport(airports, aircrafts[i].destination_airport)
            if airport_destination != -1:
                if airport_destination.schengen:
                    color = "ffffc9e1"
                else:
                    color = "ffc9ffcc"
                f.write(f"""    
                            <Placemark>
                                <name>{aircrafts[i].aircraft_id} (LEBL to {aircrafts[i].destination_airport})</name>
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
                                        {LEBL.longitude},{LEBL.latitude},0 {airport_destination.longitude},{airport_destination.latitude},0
                                    </coordinates>
                                </LineString>
                            </Placemark>
                                """)
            i += 1
        f.write("</Document>\n</kml>")
    return filename


def MapLongDistanceFlights(aircrafts, airports, filename="flights.kml"):
    LEBL = FindAirport(airports, "LEBL")
    # Si LEBL no està al file d'aeroports que marqui error
    if LEBL == -1:
        print("Error: LEBL coordinates not found in the airports list. Cannot plot trajectories.")
        return -1

    # Agafem la llista de vols de llarga distància
    Long_Flights = LongDistanceArrivals(aircrafts, airports)

    # Si per alguna raó dona error o no hi ha vols parem
    if Long_Flights == -1 or len(Long_Flights) == 0:
        print("Error: Long distance flights not found.")
        return -1

    with open(filename, "w") as f:
        f.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
        f.write('<Document>\n')
        f.write('<name>Flight Trajectories to LEBL</name>\n')

        i = 0
        # Crea l'arxiu kml recorrent els vols de llarga distància
        while i < len(Long_Flights):
            airport_origin = FindAirport(airports, Long_Flights[i].origin_airport)
            if airport_origin != -1:
                if airport_origin.schengen:
                    color = "ffffc9e1"
                else:
                    color = "ffc9ffcc"
                f.write(f"""    
                            <Placemark>
                                <name>{Long_Flights[i].aircraft_id} ({Long_Flights[i].origin_airport} to LEBL)</name>
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

def LongDistanceArrivals(aircrafts,airports):
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
    aircrafts = LoadArrivals("Arrivals.txt")
    airports_list = airport.LoadAirports("Airports.txt")
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
        plt.show()
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
