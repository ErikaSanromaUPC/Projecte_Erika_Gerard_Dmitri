def IsSchengenAirport(code):
    Schengen_prefixes = ['LO', 'EB', 'LK', 'LC', 'EK', 'EE', 'EF', 'LF', 'ED', 'LG', 'EH', 'LH','BI','LI', 'EV', 'EY', 'EL', 'LM', 'EN', 'EP', 'LP', 'LZ', 'LJ', 'LE', 'ES','LS']
    prefix=code[:2]
    if not code or len(code) < 2:
        return False
    elif prefix in Schengen_prefixes: #TODO: Canviar per un while
        return True
    else:
        return False

class Airport:
    def __init__(self, code, latitude, longitude):
        self.code=code
        self.latitude=latitude
        self.longitude=longitude
        self.schengen=IsSchengenAirport(code)

def SetSchengen(airport):
    airport.schengen=IsSchengenAirport(airport.code)

def PrintAirport(airports):
    print(f"icao Code:   {airports.code}")
    print(f"Coordinates: latitude = {airports.latitude}, longitude = {airports.longitude}")
    print(f"Schengen:    {airports.schengen}")

def ParseCoordinate(coords_airport_txt): #Passa de 'N635906' a decimals
    direction = coords_airport_txt[0]
    seconds = int(coords_airport_txt[-2:]) #Agafa els últims 2 nombres que són els segons
    minutes = int(coords_airport_txt[-4:-2]) #Agafa els següents 2 nombres que són els minuts
    degrees = int(coords_airport_txt[1:-4]) #Agafa els nombres que queden que són les hores

    decimal = degrees + (minutes / 60) + (seconds / 3600)
    if direction in ['S', 'W']:
        decimal = -decimal
    return decimal


def LoadAirports(filename):
    airports_list = []
    try:
        with open(filename, 'r') as airports_file:
            data = airports_file.read() #data és per llegir totes les línies del text
            Lines = data.splitlines() #Lines és per separar cada línia del text
            i=1
            while i < len(Lines): #TODO: fer que si el format està malament que se salti la línia
                parts=Lines[i].split()
                if len(parts) == 3:
                    code = parts[0]
                    if parts[1][0] == "N" or parts[1][0] == "S":
                        # Utilitzem la funció creada per convertir a decimals
                        lat_decimal = ParseCoordinate(parts[1])
                        lon_decimal = ParseCoordinate(parts[2])
                    else:
                        lat_decimal = float(parts[1])
                        lon_decimal = float(parts[2])
                    new_airport = Airport(code, lat_decimal, lon_decimal)
                    airports_list.append(new_airport)
                i+=1
    except FileNotFoundError:
        return []
    return airports_list


def SaveSchengenAirports(airports, filename):
    if not airports:
        return 0
    # Filtrem els aeroports que son Schengen
    schengen_list = []
    i = 0
    while i < len(airports):
        airport_i = airports[i]
        if airport_i.schengen: #Si és Schengen el guarda a la llista Schengen
            schengen_list.append(airport_i)
        i += 1
    if not schengen_list:
        return 0
    with open(filename, "w") as f:
        f.write("CODE LAT LON\n")
        j=0
        while j<len(schengen_list):
            Line = schengen_list[j]
            f.write(f"{Line.code} {Line.latitude} {Line.longitude}\n")
            j+=1
    return len(schengen_list)

def AddAirport(airports, airport):
    # Comprovem si el codi ja existeix per no duplicar
    i=0
    while i < len(airports):
        if airports[i].code == airport.code:
            return False
        i+=1
    airports.append(airport) #En cas no existir, l'afegim
    return True


def RemoveAirport(airports, code):
    i = 0
    while i < len(airports):
        if airports[i].code == code: #Trobem l'aeroport que volem eliminar
            airports.pop(i)  #L'eliminem
            return 0
        i += 1
    return -1 #En cas de no trobar-lo retornem -1 que donarà error

import matplotlib.pyplot as plt

def PlotAirports (airports): #TODO: S'ha de posar amb 2 barres stacked
    schengen=0
    i=0
    while i < len(airports):
        if airports[i].schengen: #No fa falta posar ==True perquè així ja vol dir que és True
            schengen += 1
        i+=1
    non_schengen=len(airports)-schengen

    plt.bar(["Schengen", "No Schengen"], [schengen, non_schengen], color=["#e1c9ff", "#ccffc9"])
    plt.title("Schengen vs Non-Schengen Airports")
    plt.ylabel("Number of airports")
    plt.show()

def MapAirports(airports, filename="airports.kml"):
    with open (filename, "w") as f:
     #  f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
        f.write('<Document>\n')

        i=0
        while i < len(airports):
            if airports[i].schengen:
                color = "ffffc9e1"
            else:
                color = "ffc9ffcc"
            f.write(f"""
            <Placemark>
            <name>{airports[i].code}</name>
            <Style><IconStyle><color>{color}</color></IconStyle></Style>
            <Point><coordinates>{airports[i].longitude},{airports[i].latitude},0</coordinates></Point>
            </Placemark>
            """)
            i+=1
        f.write("</Document>\n</kml>")
    return filename
