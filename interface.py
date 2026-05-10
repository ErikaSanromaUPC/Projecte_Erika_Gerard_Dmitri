import tkinter as tk
from tkinter import filedialog, messagebox
from airport import *
from aircraft import *
from LEBL import * # Importa tus clases BarcelonaAP, Terminal, etc.
import os
import platform

airports = []
arrivals = []
bcn_airport = None

def load_airports(): #Obre un diàleg per carregar l'arxiu d'airports i actualitza la llista
    filename = filedialog.askopenfilename()
    if filename:
        global airports #Això fa que agafi airports principal
        airports = LoadAirports(filename)
        show_airports()

def save_schengen(): #Filtra i guarda els aeroports Schengen en un txt
    if not airports:
        messagebox.showwarning("Warning", "No airports loaded to filter.")
        return
    filename = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
    if filename:
        res = SaveSchengenAirports(airports, filename)
        if res != -1:
            messagebox.showinfo("Success", f"{res} Schengen airports have been saved.")
        else:
            messagebox.showwarning("Warning", "No Schengen airports were found in the list.")

def add_airport(): #Recull les dades dels campos d'entrada i afegeix un nou aeroport a la lista
    try:
        code = code_entry.get().upper().strip()
        lat = float(lat_entry.get())
        lon = float(lon_entry.get())
        if len(code) < 3:
            messagebox.showwarning("Error", "The ICAO code must be 3-4 characters long.")
            return
        a = Airport(code, lat, lon)
        # AddAirport retorna True si no estava repetit
        if AddAirport(airports, a):
            show_airports()
            # Netegem entrades pel següent
            code_entry.delete(0, tk.END)
            lat_entry.delete(0, tk.END)
            lon_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Error", f"Airport {code} already exists in the list.")

    except ValueError:
        messagebox.showerror("Data Error", "Please enter valid numbers for Latitude and Longitude.")

def remove_airport(): #Elimina un aeroport de la lista buscant-lo pel seu codi ICAO.
    code = code_entry.get().upper().strip()
    if RemoveAirport(airports, code) == 0:
        show_airports()
        code_entry.delete(0, tk.END)
    else:
        messagebox.showwarning("Error", f"Airport not found {code}.")

def plot_airports():
    if not airports:
        messagebox.showwarning("Warning", "Empty list.")
        return
    PlotAirports(airports)

def map_airports():
    if not airports:
        messagebox.showwarning("Warning", "Empty list.")
        return
    filename = "airports_display.kml"
    MapAirports(airports, filename)
    if messagebox.askyesno("Map Generated", f"File {filename} created. Open in Google Earth?"):
        try:
            if platform.system() == "Windows":
                os.startfile(filename)
            elif platform.system() == "Darwin":
                os.system(f"open {filename}")
            else:
                os.system(f"xdg-open {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Error opening file: {e}")

def show_airports():
    text.delete("1.0", tk.END) #Això borra tot, perquè no s'apilin els aeroports carregats
    if not airports:
        text.insert(tk.END, "No airports loaded.")
        return
    i=0
    while i < len(airports):
        airport = airports[i]
        # Utilitzem :.4f per posar 4 decimals
        text.insert(tk.END,f"{airport.code:6} | Lat: {airport.latitude:>8.4f} | Lon: {airport.longitude:>8.4f} | Schengen: {airport.schengen}\n") #Es veu amb moltes coses perquè està posat amb un format bonic
        i+=1

def load_arrivals(): #Càrrega el file d'arrivals (Arrivals.txt)."
    filename = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if filename:
        global arrivals
        arrivals = LoadArrivals(filename)
        messagebox.showinfo("Success", f"Loaded {len(arrivals)} flight arrivals.")

def plot_arrivals():
    if not arrivals:
        messagebox.showwarning("Warning", "No arrivals loaded.")
        return
    PlotArrivals(arrivals)

def plot_airlines():
    if not arrivals:
        messagebox.showwarning("Warning", "No arrivals loaded.")
        return
    PlotAirlines(arrivals)

def plot_type():
    if not arrivals:
        messagebox.showwarning("Warning", "No arrivals loaded.")
        return
    PlotFlightsType(arrivals)

def map_flights(): #Genera el mapa KML de trajectories cap a LEBL.
    if not arrivals or not airports:
        messagebox.showwarning("Warning", "Need both airports and arrivals loaded.")
        return
    filename = "flights_trajectories.kml"
    res = MapFlights(arrivals, airports, "flights_trajectories.kml")
    if res != -1:
        # Preguntem a l'usuari si el vol obrir ara
        if messagebox.askyesno("Success", f"KML '{filename}' created. Do you want to open it now?"):
            try:
                if platform.system() == "Windows":
                    os.startfile(filename)
                elif platform.system() == "Darwin":  # macOS
                    os.system(f"open {filename}")
                else:  # Linux
                    os.system(f"xdg-open {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {e}")

def check_long_distance(): #Mostra en una nova finestra els vols que requereixen inspecció (>2000km).
    if not arrivals or not airports:
        messagebox.showwarning("Warning", "Need both airports and arrivals loaded.")
        return
    long_dist = LongDistanceArrivals(arrivals, airports)

    # Obre una finestra nova per mostrar els resultats
    top = tk.Toplevel(root)
    top.title("Special Inspection (>2000km)")
    t = tk.Text(top, height=15, width=50)
    t.pack(padx=10, pady=10)

    if not long_dist or long_dist == -1:
        t.insert(tk.END, "No aircrafts require special inspection.")
    else:
        t.insert(tk.END, f"Found {len(long_dist)} aircrafts:\n" + "-" * 30 + "\n")
        i = 0
        while i < len(long_dist):
            t.insert(tk.END, f"ID: {long_dist[i].aircraft_id} from {long_dist[i].origin_airport}\n")
            i += 1

def load_lebl_structure(): # Carrega l'arxiu LEBL.txt i genera l'estructura.
    filename = filedialog.askopenfilename()
    if filename:
        global bcn_airport
        bcn_airport = LoadAirportStructure(filename)
        if bcn_airport != -1:
            messagebox.showinfo("Success", f"LEBL structure loaded. {len(bcn_airport.terminals)} terminals found.")
        else:
            messagebox.showerror("Error", "Could not load LEBL structure.")


def assign_gates_to_arrivals(): #Assigna gates a tots els vols carregats.
    if not bcn_airport or not arrivals:
        messagebox.showwarning("Warning", "Load LEBL structure and Arrivals first!")
        return

    assigned_count = 0
    i = 0
    while i < len(arrivals):
        gate_name = AssignGate(bcn_airport, arrivals[i])
        if gate_name != -1:
            assigned_count += 1
        i += 1
    messagebox.showinfo("Assignment Complete", f"Assigned {assigned_count}/{len(arrivals)} aircrafts to gates.")


def plot_gate_occupancy():
    if not bcn_airport:
        messagebox.showwarning("Warning", "LEBL structure not loaded.")
        return

    # Llamamos directamente a la función que dibuja el mapa tipo esquema
    # que pusimos en LEBL.py
    plot_airport_schema(bcn_airport)

root = tk.Tk()
root.title("Airport Manager v2 (Erika, Gerard, Dmitri)")
root.geometry("850x650")

# Contenedor pels botons superiors (dividit en 2 columnes)
top_frame = tk.Frame(root)
top_frame.pack(side="top", fill="x", padx=10, pady=5)

# Frame per Aeroports (Esquerra)
frame_left = tk.LabelFrame(top_frame, text=" Airport Management ", padx=10, pady=10)
frame_left.pack(side="left", fill="both", expand=True, padx=5)

tk.Button(frame_left, text="Load Airports", command=load_airports).pack(fill="x", pady=2)
tk.Button(frame_left, text="Save Schengen List", command=save_schengen).pack(fill="x", pady=2)
tk.Button(frame_left, text="Plot Schengen Distribution", command=plot_airports).pack(fill="x", pady=2)
tk.Button(frame_left,text="Generate Airport Map (KML)", command=map_airports).pack(fill="x", pady=2)

# Sub secció per afegir/treure aeroports
entry_frame = tk.Frame(frame_left)
entry_frame.pack(pady=5)

tk.Label(entry_frame, text="ICAO Code:").grid(row=0, column=0)
code_entry = tk.Entry(entry_frame, width=10)
code_entry.grid(row=0, column=1)

tk.Label(entry_frame, text="Lat:").grid(row=1, column=0)
lat_entry = tk.Entry(entry_frame, width=10)
lat_entry.grid(row=1, column=1)

tk.Label(entry_frame, text="Lon:").grid(row=2, column=0)
lon_entry = tk.Entry(entry_frame, width=10)
lon_entry.grid(row=2, column=1)

# Botons per afegir i eliminar aeroports
tk.Button(frame_left, text="Add New Airport", command=add_airport).pack(fill="x")
tk.Button(frame_left, text="Remove by Code", command=remove_airport).pack(fill="x", pady=2)

# Frame per flights (Dreta)
frame_right = tk.LabelFrame(top_frame, text=" Flight & Arrival Tools ", padx=10, pady=10)
frame_right.pack(side="right", fill="both", expand=True, padx=5)

tk.Button(frame_right, text="Load Arrivals File", command=load_arrivals).pack(fill="x", pady=2)
tk.Button(frame_right, text="Plot Arrival Frequency", command=plot_arrivals).pack(fill="x", pady=2)
tk.Button(frame_right, text="Plot Flights per Airline", command=plot_airlines).pack(fill="x", pady=2)
tk.Button(frame_right, text="Plot Schengen Origin Flights", command=plot_type).pack(fill="x", pady=2)
tk.Button(frame_right, text="Map Flight Trajectories (KML)", command=map_flights).pack(fill="x", pady=2)
tk.Button(frame_right, text="Check Long Distance Flights", command=check_long_distance).pack(fill="x", pady=2)

# Secció inferior per veure les dades
display_frame = tk.LabelFrame(root, text=" Data Console ")
display_frame.pack(side="bottom", fill="both", expand=True, padx=15, pady=10)

# Àrea de text central perquè quedi més bonic
text = tk.Text(display_frame, height=15,  font=("Courier", 10))
text.pack(side="left", fill="both", expand=True)

# Frame per LEBL Gate Management (Centre o Dreta)
frame_gates = tk.LabelFrame(top_frame, text=" LEBL Gate Management ", padx=10, pady=10)
frame_gates.pack(side="left", fill="both", expand=True, padx=5)

tk.Button(frame_gates, text="Load LEBL Structure", command=load_lebl_structure, bg="#d1e7ff").pack(fill="x", pady=2)
tk.Button(frame_gates, text="Assign Gates to Flights", command=assign_gates_to_arrivals).pack(fill="x", pady=2)
tk.Button(frame_gates, text="Show Gate Occupancy (Extra)", command=plot_gate_occupancy, bg="#fff2cc").pack(fill="x", pady=2)

root.mainloop()
