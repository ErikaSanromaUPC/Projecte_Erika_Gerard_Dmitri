import os
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
    if not os.path.exists(filename): #Prova que el fitxer existeixi
        print(f"Error: Fitxer {filename} no trobat.")
        return -1
    terminal.airlines = []  # Dropping previous list
    try:
        with open(filename, 'r') as f:
            data = f.read() #data és per llegir totes les línies del text
            lines = data.splitlines()
            i = 0
            while i < len(lines):
                parts = lines[i].strip().split('\t')  # Format: Nom \t ICAO strip treu els esapis dels extrems
                if len(parts) >= 2:
                    icao_code = parts[1]
                    terminal.airlines.append(icao_code)
                i += 1
        return 0
    except Exception as e:
        print(f"Error reading airlines: {e}")
        return -1