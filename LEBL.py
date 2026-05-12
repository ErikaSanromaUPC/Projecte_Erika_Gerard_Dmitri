import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
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