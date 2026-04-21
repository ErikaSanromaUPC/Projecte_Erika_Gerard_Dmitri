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

