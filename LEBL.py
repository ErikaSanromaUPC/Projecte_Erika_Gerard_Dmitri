import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from aircraft import Aircraft

class Gate:
    def __init__(self, name):
        self.name = name
        self.occupied = False
        self.aircraft_id = "" # ID de l'avió si està ocupada

class BoardingArea:
    def __init__(self, name, area_type):
        self.name = name
        self.type = area_type # "Schengen" o "non-Schengen"
        self.gates = []

class Terminal:
    def __init__(self, name):
        self.name = name
        self.boarding_areas = []
        self.airlines = [] # Llista de codis ICAO de les aerolínies

class BarcelonaAP:
    def __init__(self, code):
        self.code = code
        self.terminals = []

def SetGates(area, init_gate, end_gate, prefix): #Crea la llista de portes per a una àrea específica
    if end_gate <= init_gate:
        return -1
    area.gates = []
    i = init_gate
    while i <= end_gate: # Recorre totes les gates de la BA
        gate_name = f"{prefix}{i}"
        new_gate = Gate(gate_name)
        area.gates.append(new_gate)
        i += 1
    return 0

def LoadAirlines(terminal,t_name): # Llegeix les aerolinies dels txt
    filename = f"{t_name}_Airlines.txt" # Crea el nom del fitxer que ha d'obrir
    try:
        with open(filename, 'r') as f:
            terminal.airlines = []
            data = f.read() #data és per llegir totes les línies del text
            lines = data.splitlines()
            i = 0
            while i < len(lines):
                parts = lines[i].strip().split('\t')  # Format: Nom \t ICAO strip treu els espaxis dels extrems
                if len(parts) >= 2:
                    icao_code = parts[1]
                    terminal.airlines.append(icao_code)
                i += 1
        return 0
    except FileNotFoundError:
        print(f"Error: Fitxer {filename} no trobat.")
        return -1
    except Exception as e:
        print(f"Error reading airlines: {e}")
        return -1

def LoadAirportStructure(filename):
    """Construeix tota l'estructura de l'aeroport des de LEBL.txt."""
    try:
        with open(filename, 'r') as f:
            lines = f.readlines()

        # Línia 1: Codi Aeroport i número de terminals
        first_line = lines[0].split() #[LEBL ,2, terminals]
        bcn = BarcelonaAP(first_line[0])
        num_terminals = int(first_line[1])

        current_line = 1
        terminals_processed = 0
        while terminals_processed <num_terminals:
            # Línia de Terminal: Terminal T1 5 boarding areas
            t_parts = lines[current_line].split()
            t_name = t_parts[1]
            num_areas = int(t_parts[2])
            new_terminal = Terminal(t_name)
            LoadAirlines(new_terminal, t_name)  # Carrega aerolínies per aquesta terminal
            current_line += 1
            areas_processed=0
            while areas_processed<num_areas:
                # Línia d'Àrea: Area A Schengen Gates 1 - 11
                a_parts = lines[current_line].split()
                area_name = a_parts[1].lower() #Ho posa en minuscules pel prefix
                area_type = a_parts[2]
                init_g = int(a_parts[4])
                end_g = int(a_parts[6])

                new_area = BoardingArea(area_name, area_type)
                # El prefix serà: NomTerminal_NomArea_G (ex: T1BAaG1)
                prefix = f"{t_name}BA{area_name}G"
                SetGates(new_area, init_g, end_g, prefix)

                new_terminal.boarding_areas.append(new_area)
                current_line += 1
                areas_processed += 1

            bcn.terminals.append(new_terminal)
            terminals_processed += 1

        return bcn
    except FileNotFoundError:
        return -1
    except Exception as e:
        print(f"Error carregant l'estructura: {e}")
        return -1

def GateOccupancy (bcn):
    gates=[]
    i=0
    while i<len(bcn.terminals):
        j=0
        while j<len(bcn.terminals[i].boarding_areas):
            area=bcn.terminals[i].boarding_areas[j]
            k=0
            while k<len(area.gates):
                gate=area.gates[k]
                if gate.occupied:
                    gates.append((gate.name, "occupied", gate.aircraft_id))
                else:
                    gates.append((gate.name, "free", None))
                k=k+1
            j=j+1
        i=i+1
    return gates

def IsAirlineInTerminal(terminal, name):
    # 1. Si el nombre es un "null string" (vacío), devolvemos False y código -1
    if name == "":
        return False, -1

    # Obtenemos la lista y su longitud
    aerolineas = terminal.airlines
    indice = 0
    cantidad = len(aerolineas)

    # 2. Recorremos la lista manualmente (si está vacía, no entra al while)
    while indice < cantidad:
        if aerolineas[indice] == name:
            return True, 0  # Encontrada, código 0 (sin error)
        indice += 1

    # 3. Si no la encuentra o la lista estaba vacía
    return False, 0  # No encontrada, código 0 (sin error)

def SearchTerminal(bcn, airline_code):
    """Busca en qué terminal opera una aerolínea."""
    terminales = bcn.terminals
    indice = 0
    cantidad = len(terminales)
    while indice < cantidad:
        t = terminales[indice]

        # Atrapamos los dos valores que ahora devuelve la función ayudante
        existe, codigo_error = IsAirlineInTerminal(t, airline_code)

        # Solo comprobamos la variable 'existe'
        if existe == True:
            return t.name

        indice += 1

    return ""

def AssignGate(bcn, aircraft): #Busca la primera porta lliure segons terminal i tipus de vol.
    from airport import IsSchengenAirport  # Import local per evitar líos
    # 1. Trobar terminal per l'aerolínia
    t_name = SearchTerminal(bcn, aircraft.airline)
    if not t_name:
        return -1  # Aerolínia no trobada a cap terminal

    # 2. Tipus de vol (Schengen o no)
    if IsSchengenAirport(aircraft.origin_airport):
        required_type = "Schengen"
    else:
        required_type = "non-Schengen"

    # 3. Buscar porta a la terminal i àrea correcta
    i=0
    while i<len(bcn.terminals):
        if t_name == bcn.terminals[i].name: #recorre fins que coincideix la terminal
            j=0
            while j<len(bcn.terminals[i].boarding_areas):
                area=bcn.terminals[i].boarding_areas[j]
                if area.type==required_type:    #busca si es schengen o no
                    k=0
                    while k<len(area.gates):
                        if not area.gates[k].occupied: #que no estigui ocupada
                            area.gates[k].occupied=True
                            area.gates[k].aircraft_id=aircraft.aircraft_id
                            return area.gates[k].name
                        k=k+1
                j=j+1
        i=i+1
    return -1  # Per si no hi ha portes lliures


def plot_airport_schema(bcn):  # Dibuixar mapa visual
    if not bcn:
        return

    fig, ax = plt.subplots(figsize=(16, 10))
    ax.set_title(f"Airport Map: {bcn.code}", fontsize=18, fontweight='bold', pad=20) #TÍTOL

    terminal_x = 0 #POSICIÓ 0 DEL PAPER
    gate_width = 0.5 #MIDA DE LES GATES
    gate_height = 0.25

    # 1. Bucle per dibuixar les terminals
    t_idx = 0
    while t_idx < len(bcn.terminals):
        terminal = bcn.terminals[t_idx]
        num_areas = len(terminal.boarding_areas)
        t_width = num_areas * 5 #AMPLADA DE LA TERMINAL EN BASE A LES AREES QUE TENIM

        # Passadís horitzontal
        main_corridor = patches.Rectangle((terminal_x, 15), t_width, 0.6, color='#1a5276') #PASSADÍS PRINCIPAL
        ax.add_patch(main_corridor)
        ax.text(terminal_x, 15.8, terminal.name, fontsize=16, fontweight='bold', color='#1a5276')

        # 2. Bucle per dibuixar les Boarding Areas
        a_idx = 0
        while a_idx < num_areas:
            area = terminal.boarding_areas[a_idx]
            area_x_center = terminal_x + (a_idx * 5) + 2.5

            # Passadís vertical
            area_corridor = patches.Rectangle((area_x_center - 0.2, 2), 0.4, 16, color='#34495e', alpha=0.8)
            ax.add_patch(area_corridor)
            ax.text(area_x_center - 0.8, 1.2, f"BA {area.name.upper()}", fontsize=11, fontweight='bold')

            # 3. Bucle de Gates
            g_idx = 0
            while g_idx < len(area.gates):
                gate = area.gates[g_idx]

                #CÀLCUL DE POSICIÓ
                if g_idx % 2 == 0:
                    side = -1  # Esquerra
                else:
                    side = 1  # Dreta

                level = 14.2 - (g_idx // 2) * 0.40 #ALÇADA DE LA PORTA

                if level >= -10:
                    #CÀLCUL DE GATE_X
                    if side == -1:
                        gate_x = area_x_center + (side * 0.8) - (gate_width / 2) #pels rectangles
                    else:
                        gate_x = area_x_center + (side * 0.8)

                    #COLOR
                    if gate.occupied:
                        color = '#e74c3c'  # Vermell
                    else:
                        color = '#2ecc71'  # Verd

                    rect = patches.Rectangle((gate_x, level), gate_width, gate_height, color=color, zorder=3)
                    ax.add_patch(rect)

                    # Línia de connexió al passadís
                    ax.plot([area_x_center, gate_x + gate_width / 2],
                            [level + gate_height / 2, level + gate_height / 2],
                            color='#7f8c8d', lw=1, zorder=1)

                    # Text del avió
                    if gate.occupied:
                        #ALINEACIÓ TEXT
                        if side == -1:
                            ha_value = 'right'
                        else:
                            ha_value = 'left'

                        ax.text(gate_x + side * 0.1, level + gate_height/2, gate.aircraft_id, fontsize=5,
                                ha=ha_value, fontweight='bold', color='black')
                        ax.text(gate_x, level + 0.3, gate.name.split('G')[-1], fontsize=6, color='gray')
                    else:
                        if side == -1:
                            ha_value = 'right'
                        else:
                            ha_value = 'left'

                        # Número de la gate
                        ax.text(gate_x + side * 0.1, level + gate_height / 2, gate.name, fontsize=4, ha=ha_value, color='gray', fontstyle='italic')

                g_idx += 1  # Incrementar index gates
            a_idx += 1  # Incrementar index àrees

        terminal_x += t_width + 4
        t_idx += 1  # Incrementar index terminals

    ax.set_xlim(-2, terminal_x)
    ax.set_ylim(0, 17)
    ax.axis('off')
    plt.tight_layout()
    plt.show()


def MergeMovements(arrivals, departures):
    """Combina llistes d'arribades i sortides en una llista única basánt-se en l'ID de l'avió."""
    if len(arrivals) == 0 or len(departures) == 0:
        return [], -1

    merged_list = []

    # 1. Copia tots els arrivals a la nova llista merged_list
    i = 0
    while i < len(arrivals):
        arr = arrivals[i]
        # Creem una còpia per no alterar la llista original
        new_aircraft = Aircraft(arr.aircraft_id, arr.airline, arr.origin_airport, arr.arrival_time)
        new_aircraft.arrival_time = arr.arrival_time
        merged_list.append(new_aircraft)
        i += 1

    # 2. Recorre els departures i busca si coincideix amb algun arrival existent
    j = 0
    while j < len(departures):
        dep = departures[j]
        found = False
        k = 0
        while k < len(merged_list):
            existing = merged_list[k]
            # Si coincideixen en ID i l'avió arriba abans de departure
            if existing.aircraft_id == dep.aircraft_id:
                if existing.arrival_time < dep.departure_time:
                    # Mesclem les dades
                    existing.destination_airport = dep.destination_airport #La destination de l'arrival = La destinació del departure
                    existing.departure_time = dep.departure_time #Temps departure de l'arrival = Temps departure del departure
                    found = True
            k += 1
        # Si no s'ha trobat cap, és un avió nocturn ("night aircraft")
        if not found:
            night_aircraft = Aircraft(dep.aircraft_id, dep.airline, "")
            night_aircraft.destination_airport = dep.destination_airport
            night_aircraft.departure_time = dep.departure_time
            merged_list.append(night_aircraft)

        j += 1

    return merged_list, 0


def NightAircraft(aircrafts):
    """Retorna avions que NOMÉS tenen dades de sortida (han passat la nit a l'aeroport)."""
    if len(aircrafts) == 0:
        return [], -1
    night_list = []
    i = 0
    while i < len(aircrafts):
        actual_aircraft = aircrafts[i]
        #Si té hora de sortida però NO d'arribada
        if actual_aircraft.departure_time != "" and actual_aircraft.arrival_time == "":
            night_list.append(actual_aircraft)
        i += 1
    return night_list, 0


def AssignNightGates(bcn, aircrafts):
    """Assigna gates al principi del dia als Night aircrafts, retorna cquantes gates s'han assignat"""
    if len(aircrafts) == 0:
        return -1

    assigned_count = 0
    i = 0
    while i < len(aircrafts):
        actual_aircraft = aircrafts[i]
        # NOMÉS avions amb sortida establerta i arribada buida
        if actual_aircraft.departure_time != "" and actual_aircraft.arrival_time == "":
            gate_name = AssignGate(bcn, actual_aircraft)
            if gate_name != -1:
                assigned_count += 1
        i += 1
    return assigned_count


def FreeGate(bcn, aircraft_id):
    """Busca un avió per ID en tot l'aeroport i allibera la gate"""
    i = 0
    while i < len(bcn.terminals):
        terminal_actual = bcn.terminals[i]
        j = 0
        while j < len(terminal_actual.boarding_areas):
            area = terminal_actual.boarding_areas[j]
            k = 0
            while k < len(area.gates):
                gate = area.gates[k]
                if gate.occupied and gate.aircraft_id == aircraft_id:
                    gate.occupied = False
                    gate.aircraft_id = ""
                    return 0 # Gate alliberada
                k += 1
            j += 1
        i += 1
    return -1 #Error Avió no trobat a cap gate


def AssignGatesAtTime(bcn, aircrafts, current_time):
    """Allibera gates d'avions que ja s'han enlairat i assigna noves gates per una franja d'1 hora"""
    # current_time ve en format "01:00", "02:00", ...
    start_hour = int(current_time.split(':')[0])

    # 1. ALLIBERAR GATES: Buscar quins avions programats s'enlairen a aquesta hora
    i = 0
    while i < len(aircrafts):
        actual_aircraft = aircrafts[i]
        if actual_aircraft.departure_time != "":
            departure_hour = int(actual_aircraft.departure_time.split(':')[0])
            if departure_hour == start_hour:
                FreeGate(bcn, actual_aircraft.aircraft_id)
        i += 1

    # 2. ASSIGNAR GATES: Buscar quins avions aterren en aquesta franja d' 1 hora
    unassigned_count = 0
    j = 0
    while j < len(aircrafts):
        actual_aircraft = aircrafts[j]
        if actual_aircraft.arrival_time != "":
            arrival_hour = int(actual_aircraft.arrival_time.split(':')[0])
            if arrival_hour == start_hour:
                gate_name = AssignGate(bcn, actual_aircraft)
                if gate_name == -1:
                    unassigned_count += 1 # No cap per falta d'espai
        j += 1
    return unassigned_count


def PlotDayOccupancy(bcn, aircrafts):
    """Pinta l'ocupació horaria i les falles d'assignació al llarg del dia."""
    # Inicialitzem llistes de 24 posiciones per guardar dades de cada hora
    hours_labels = []
    t1_occupancy = []
    t2_occupancy = []
    rejected_flights = []

    # IMPORTANT: Per simular el día net, carreguem de nou els de la nit primer
    # (Assumint que el bcn que entra està net d'arrivals)

    h = 0
    while h < 24:
        # Posa en formar d'hora: "00:00", "01:00"...
        if h < 10:
            time_str = f"0{h}:00"
        else:
            time_str = f"{h}:00"

        hours_labels.append(time_str)

        # Executem l'assignaciño d'aquella hora
        unassigned = AssignGatesAtTime(bcn, aircrafts, time_str)
        rejected_flights.append(unassigned)

        # Comptem quantes gates té ocupades la T1 i la T2 en aquest moment
        t1_count = 0
        t2_count = 0

        # Recompte manual T1
        areas_t1 = bcn.terminals[0].boarding_areas
        a = 0
        while a < len(areas_t1):
            gates = areas_t1[a].gates
            g = 0
            while g < len(gates):
                if gates[g].occupied:
                    t1_count += 1
                g += 1
            a += 1

        # Recompte manual T2
        areas_t2 = bcn.terminals[1].boarding_areas
        a = 0
        while a < len(areas_t2):
            gates = areas_t2[a].gates
            g = 0
            while g < len(gates):
                if gates[g].occupied:
                    t2_count += 1
                g += 1
            a += 1

        t1_occupancy.append(t1_count)
        t2_occupancy.append(t2_count)
        h += 1

    # --- PINTAR EL PLOT ---
    plt.figure(figsize=(14, 6))
    plt.plot(hours_labels, t1_occupancy, label='T1 Occupied Gates', color='#1a5276', marker='o')
    plt.plot(hours_labels, t2_occupancy, label='T2 Occupied Gates', color='#e67e22', marker='s')
    plt.bar(hours_labels, rejected_flights, label='Rejected Flights (Full)', color='#e74c3c', alpha=0.6)

    plt.title("LEBL 24-Hour Dynamic Simulation Status", fontsize=14, fontweight='bold')
    plt.xlabel("Hour of the Day")
    plt.ylabel("Number of Aircrafts / Gates")
    plt.xticks(rotation=45)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend()
    plt.tight_layout()
    plt.show()


# --- TEST SECTION ---
if __name__ == "__main__":

    # TEST 1: SetGates
    area = BoardingArea("a", "Schengen")
    result = SetGates(area, 1, 5, "T1BAaG")
    print("TEST SetGates:")
    print(result)           # Esperado: 0
    print(len(area.gates))  # Esperado: 5
    print(area.gates[0].name)  # Esperado: T1BAaG1
    print()

    # TEST 2: IsAirlineInTerminal
    terminal = Terminal("T1")
    terminal.airlines = ["IBE", "VLG", "RYR"]
    print("TEST IsAirlineInTerminal:")
    print(IsAirlineInTerminal(terminal, "IBE"))  # Esperado: True, 0
    print(IsAirlineInTerminal(terminal, "AAA"))  # Esperado: False, 0
    print(IsAirlineInTerminal(terminal, ""))     # Esperado: False, -1
    print()

    # TEST 3: LoadAirportStructure
    print("TEST LoadAirportStructure:")
    bcn = LoadAirportStructure("LEBL.txt")
    print(bcn)              # Esperado: objeto BarcelonaAP, no -1
    print(bcn.code)         # Esperado: LEBL
    print(len(bcn.terminals))  # Esperado: numero de terminals
    print()

    # TEST 4: SearchTerminal
    print("TEST SearchTerminal:")
    print(SearchTerminal(bcn, "IBE"))  # Esperado: nom de la terminal
    print(SearchTerminal(bcn, "XXX"))  # Esperado: ""
    print()

    # TEST 5: GateOccupancy
    print("TEST GateOccupancy:")
    gates = GateOccupancy(bcn)
    print(len(gates))       # Esperado: total de gates
    print(gates[0])         # Esperado: (nom, "free", None)