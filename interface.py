import tkinter as tk
from tkinter import filedialog, messagebox
from airport import *
from aircraft import *
from LEBL import * # Importa classes BarcelonaAP, Terminal, etc.
import os
import platform
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

airports = []
arrivals = []
departures = []
all_movements = []
bcn_airport = None
current_canvas = None


def PrintToLog(title, message):
    """Funció auxiliar per escriure missatges de format net al log central."""
    text.delete("1.0", tk.END)
    text.insert(tk.END, f"=============================================\n")
    text.insert(tk.END, f" {title.upper()}\n")
    text.insert(tk.END, f"=============================================\n\n")
    text.insert(tk.END, f"{message}\n")
    text.insert(tk.END, f"\n" + "-" * 45 + "\n")


# FUNCIONES AUTOMÀTIQUES

def LoadAirportsAuto():
    """Carrega l'arxiu Airports.txt automàticament al arrancar si existeix."""
    global airports
    filename = "Airports.txt"
    if os.path.exists(filename):
        airports = LoadAirports(filename)
        # Mostramos los aeropuertos en la consola de texto directamente al iniciar
        ShowAirports()
        print(f"[INFO] Airports loaded automatically. Total: {len(airports)}")
    else:
        print(f"[WARN] Airports.txt not found for auto-load.")


def LoadArrivalsAuto():
    """Carrega l'arxiu Arrivals.txt automàticament al començar si existeix."""
    global arrivals
    filename = "Arrivals.txt"
    if os.path.exists(filename):
        arrivals = LoadArrivals(filename)
        print(f"[INFO] Arrivals loaded automatically. Total: {len(arrivals)}")
    else:
        print(f"[WARN] Arrivals.txt not found for auto-load.")


def LoadDeparturesAuto():
    """Carrega l'arxiu Departures.txt automàticament al arrancar si existeix."""
    global departures
    filename = "Departures.txt"
    if os.path.exists(filename):
        var_res = LoadDepartures(filename)
        departures = var_res[0]
        code = var_res[1]
        if code == 0:
            print(f"[INFO] Departures loaded automatically. Total: {len(departures)}")
        else:
            print(f"[ERROR] Could not auto-load Departures file correctly.")
    else:
        print(f"[WARN] Departures.txt not found for auto-load.")


def LoadLeblStructureAuto():
    """Carrega l'arxiu LEBL.txt automàticament al arrancar si existeix."""
    global bcn_airport
    filename = "LEBL.txt"
    if os.path.exists(filename):
        bcn_airport = LoadAirportStructure(filename)
        if bcn_airport != -1:
            print(f"[INFO] LEBL structure loaded automatically. {len(bcn_airport.terminals)} terminals found.")
        else:
            print(f"[ERROR] Could not load LEBL structure automatically.")
    else:
        print(f"[WARN] LEBL.txt not found for auto-load.")


# FUNCIONS MANUALS (Carregar a mà els files)

def LoadAirportsManual():  # Obre un diàleg per carregar l'arxiu d'airports i actualitza la llista
    filename = filedialog.askopenfilename()
    if filename:
        global airports
        airports = LoadAirports(filename)
        ShowAirports()


def SaveSchengen():  # Filtra i guarda els aeroports Schengen en un txt
    if not airports:
        messagebox.showwarning("Warning", "No airports loaded to filter.")
        return
    filename = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
    if filename:
        res = SaveSchengenAirports(airports, filename)
        if res != -1:
            PrintToLog("Schengen Filter",
                       f"Success: {res} Schengen airports have been saved to:\n{os.path.basename(filename)}")
        else:
            messagebox.showwarning("Warning", "No Schengen airports were found in the list.")


def AddAirportManual():  # Recull les dades dels campos d'entrada i afegeix un nou aeroport a la lista
    try:
        code = code_entry.get().upper().strip()
        lat = float(lat_entry.get())
        lon = float(lon_entry.get())
        if len(code) < 3:
            messagebox.showwarning("Error", "The ICAO code must be 3-4 characters long.")
            return
        a = Airport(code, lat, lon)
        if AddAirport(airports, a):
            ShowAirports()
            code_entry.delete(0, tk.END)
            lat_entry.delete(0, tk.END)
            lon_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Error", f"Airport {code} already exists in the list.")

    except ValueError:
        messagebox.showerror("Data Error", "Please enter valid numbers for Latitude and Longitude.")


def RemoveAirportManual():  # Elimina un aeroport de la lista buscant-lo pel seu codi ICAO.
    code = code_entry.get().upper().strip()
    if RemoveAirport(airports, code) == 0:
        ShowAirports()
        code_entry.delete(0, tk.END)
    else:
        messagebox.showwarning("Error", f"Airport not found {code}.")


def PlotAirportsManual():
    if not airports:
        messagebox.showwarning("Warning", "Empty list.")
        return
    plt.clf()
    PlotAirports(airports)
    EmbedPlotInGui()


def MapAirportsManual():
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


def MapLongDistanceFlightsManual():  # Genera el KML només amb els vols de llarga distància
    if not arrivals or not airports:
        messagebox.showwarning("Warning", "Need both airports and arrivals loaded.")
        return
    filename = "long_distance_trajectories.kml"
    # Crida la funció original de mapes que ja filtra internament utilitzant LongDistanceArrivals
    res = MapLongDistanceFlights(arrivals, airports, filename)
    if res != -1:
        if messagebox.askyesno("Success", f"KML '{filename}' created with long distance flights. Do you want to open it now?"):
            try:
                if platform.system() == "Windows":
                    os.startfile(filename)
                elif platform.system() == "Darwin":  # macOS
                    os.system(f"open {filename}")
                else:  # Linux
                    os.system(f"xdg-open {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {e}")


def ShowAirports():
    text.delete("1.0", tk.END)
    if not airports:
        text.insert(tk.END, "No airports loaded.")
        return
    i = 0
    while i < len(airports):
        airport = airports[i]
        text.insert(tk.END,
                    f"{airport.code:6} | Lat: {airport.latitude:>8.4f} | Lon: {airport.longitude:>8.4f} | Schengen: {airport.schengen}\n")
        i += 1


def LoadArrivalsFile():  # Càrrega el file d'arrivals (Arrivals.txt)."
    filename = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if filename:
        global arrivals
        arrivals = LoadArrivals(filename)
        PrintToLog("Arrivals Loaded", f"Successfully loaded {len(arrivals)} flight arrivals from data file.")


def PlotArrivalsManual():
    if not arrivals:
        messagebox.showwarning("Warning", "No arrivals loaded.")
        return
    plt.clf()
    PlotArrivals(arrivals)
    EmbedPlotInGui()


def PlotAirlinesManual():
    if not arrivals:
        messagebox.showwarning("Warning", "No arrivals loaded.")
        return
    plt.clf()
    PlotAirlines(arrivals)
    EmbedPlotInGui()


def PlotTypeManual():
    if not arrivals:
        messagebox.showwarning("Warning", "No arrivals loaded.")
        return
    plt.clf()
    PlotFlightsType(arrivals)
    EmbedPlotInGui()


def MapFlightsManual():  # Genera el mapa KML de trajectories cap a LEBL.
    if not arrivals or not airports:
        messagebox.showwarning("Warning", "Need both airports and arrivals loaded.")
        return
    filename = "flights_trajectories.kml"
    res = MapFlights(arrivals, airports, "flights_trajectories.kml")
    if res != -1:
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


def CheckLongDistance():  # Mostra al log els vols que requereixen inspecció (>2000km).
    if not arrivals or not airports:
        messagebox.showwarning("Warning", "Need both airports and arrivals loaded.")
        return
    long_dist = LongDistanceArrivals(arrivals, airports)
    text.delete("1.0", tk.END)

    if not long_dist or long_dist == -1:
        PrintToLog("Special Inspection (>2000km)", "No aircrafts require special inspection.")
    else:
        text.insert(tk.END, "=============================================\n")
        text.insert(tk.END, "         SPECIAL INSPECTION (>2000km)        \n")
        text.insert(tk.END, "=============================================\n")
        text.insert(tk.END, f"Found {len(long_dist)} aircrafts requiring check:\n")
        text.insert(tk.END, "-" * 45 + "\n")

        i = 0
        while i < len(long_dist):
            ac = long_dist[i]
            text.insert(tk.END, f"✈ ID: {ac.aircraft_id:8} | Origin: {ac.origin_airport:4} | Airline: {ac.airline}\n")
            i += 1

        text.insert(tk.END, "-" * 45 + "\n")
        text.insert(tk.END, "Please route these aircrafts to the inspection zone.")


def LoadLeblStructureManual():  # Carrega l'arxiu LEBL.txt i genera l'estructura.
    filename = filedialog.askopenfilename()
    if filename:
        global bcn_airport
        bcn_airport = LoadAirportStructure(filename)
        if bcn_airport != -1:
            PrintToLog("LEBL Structure",
                       f"Airport structure loaded successfully.\nFound {len(bcn_airport.terminals)} active terminals ready for simulation.")
        else:
            messagebox.showerror("Error", "Could not load LEBL structure.")


def AssignGatesToArrivals():  # Assigna gates a tots els vols carregats.
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
    PrintToLog("Gate Assignment",
                 f"Assignment process complete.\nSuccessfully routed {assigned_count}/{len(arrivals)} aircrafts to available gates.")


def PlotGateOccupancy():
    if not bcn_airport:
        messagebox.showwarning("Warning", "LEBL structure not loaded.")
        return
    plt.clf()
    plot_airport_schema(bcn_airport)
    EmbedPlotInGui()


def LoadDeparturesFile():
    """Carrèga l'arxiu de sortides."""
    filename = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if filename:
        global departures
        departures, code = LoadDepartures(filename)
        if code == 0:
            PrintToLog("Departures Loaded", f"Successfully loaded {len(departures)} schedule flight departures.")
        else:
            messagebox.showerror("Error", "Could not load departures file.")


def RunDynamicSimulation():
    """Executa la fusió i prepara els moviments del dia."""
    if not bcn_airport or not arrivals or not departures:
        messagebox.showwarning("Warning", "You need to load LEBL Structure, Arrivals and Departures first!")
        return

    ResetAirport(bcn_airport)

    global all_movements
    result_merge = MergeMovements(arrivals, departures)
    all_movements = result_merge[0]
    code = result_merge[1]

    if code == 0:
        result_night = NightAircraft(all_movements)
        night_list = result_night[0]
        night_code = result_night[1]
        if night_code == 0:
            night_assigned = AssignNightGates(bcn_airport, night_list)

            log_msg = f"Merged total operations: {len(all_movements)} daily flights.\n" \
                      f"Night aircrafts parked at gates at 00:00: {night_assigned}\n\n" \
                      f"Ready to check hourly airport maps or continuous plots."
            PrintToLog("Simulation Base Ready", log_msg)
        else:
            messagebox.showerror("Error", "Could not process night aircrafts.")
    else:
        messagebox.showerror("Error", "Could not merge movements.")


def ShowHourlyMap():
    """Llegeix l'hora de la interfície principal, simula l'estat i dibuixa el mapa."""
    if not all_movements:
        messagebox.showwarning("Warning", "Run the Dynamic Simulation fusion first!")
        return

    try:
        hour_str = hour_entry.get().strip()
        hour = int(hour_str)
        if hour < 0 or hour > 23:
            messagebox.showerror("Error", "Please enter an hour between 0 and 23.")
            return
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid number (00-23) in the hour slot.")
        return

    ResetAirport(bcn_airport)

    res_night = NightAircraft(all_movements)
    if res_night[1] == 0:
        AssignNightGates(bcn_airport, res_night[0])

    gui_waiting_list = []

    h = 0
    while h <= hour:
        if h < 10:
            time_str = f"0{h}:00"
        else:
            time_str = f"{h}:00"
        AssignGatesAtTime(bcn_airport, all_movements, time_str, gui_waiting_list)
        h += 1

    plt.clf()
    plot_airport_schema(bcn_airport)
    EmbedPlotInGui()

    status_msg = f"Airport map updated for timestamp: {hour:02d}:00.\n"
    if len(gui_waiting_list) > 0:
        status_msg += f"TAXIWAY WARNING: There are {len(gui_waiting_list)} aircrafts holding on taxiways due to full gates."
    else:
        status_msg += "TAXIWAY CLEAR: Ground traffic is moving fluently. No delays reported."

    PrintToLog(f"Status at {hour:02d}:00", status_msg)


def EmbedPlotInGui():
    """Captura la figura actual de matplotlib i la incrusta al plot_frame de la GUI."""
    global current_canvas

    if current_canvas is not None:
        current_canvas.get_tk_widget().destroy()

    fig = plt.gcf()
    current_canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    current_canvas.draw()
    current_canvas.get_tk_widget().pack(fill="both", expand=True)
    plot_frame.update_idletasks()


def ShowFullDayPlots():
    """Executa i imprimeix la gràfica lineal de les 24h."""
    if not all_movements:
        messagebox.showwarning("Warning", "Run the Dynamic Simulation fusion first!")
        return
    plt.clf()
    PlotDayOccupancy(bcn_airport, all_movements)
    EmbedPlotInGui()
    PrintToLog("Occupancy Plot", "24-Hour continuous gate occupancy analysis graph generated on the right panel.")


plt.ioff()

root = tk.Tk()
root.title("Airport Manager v2 (Erika, Gerard, Dmitri)")
root.geometry("950x650")

top_frame = tk.Frame(root)
top_frame.pack(side="top", fill="x", padx=10, pady=5)

# Frame per Aeroports (Esquerra)
frame_left = tk.LabelFrame(top_frame, text=" Airport Management ", padx=10, pady=10)
frame_left.pack(side="left", fill="both", expand=True, padx=5)

tk.Button(frame_left, text="Load Airports", command=LoadAirportsManual).pack(fill="x", pady=2)
tk.Button(frame_left, text="Save Schengen List", command=SaveSchengen).pack(fill="x", pady=2)
tk.Button(frame_left, text="Plot Schengen Distribution", command=PlotAirportsManual).pack(fill="x", pady=2)
tk.Button(frame_left, text="Generate Airport Map (KML)", command=MapAirportsManual).pack(fill="x", pady=2)

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

tk.Button(frame_left, text="Add New Airport", command=AddAirportManual).pack(fill="x")
tk.Button(frame_left, text="Remove by Code", command=RemoveAirportManual).pack(fill="x", pady=2)

# Frame per LEBL Gate Management (Centre)
frame_gates = tk.LabelFrame(top_frame, text=" LEBL Gate Management ", padx=10, pady=10)
frame_gates.pack(side="left", fill="both", expand=True, padx=5)

tk.Button(frame_gates, text="1. Load LEBL Structure (Optional)", command=LoadLeblStructureManual, bg="#d1e7ff").pack(fill="x", pady=2)
tk.Button(frame_gates, text="2. Load Departures File", command=LoadDeparturesFile, bg="#d1e7ff").pack(fill="x", pady=2)
tk.Button(frame_gates, text="3. Merge & Run Simulation Base", command=RunDynamicSimulation, bg="#d4edda").pack(fill="x", pady=2)
tk.Button(frame_gates, text="4. Plot 24h Occupancy Graphs", command=ShowFullDayPlots, bg="#fff2cc").pack(fill="x", pady=2)

hour_select_frame = tk.Frame(frame_gates)
hour_select_frame.pack(fill="x", pady=5)

tk.Label(hour_select_frame, text="Target Hour (00-23):", font=("Arial", 9, "bold")).pack(side="left", padx=2)
hour_entry = tk.Entry(hour_select_frame, width=5, justify="center")
hour_entry.pack(side="left", padx=5)
hour_entry.insert(0, "12")

tk.Button(frame_gates, text="5. View Map at Custom Hour", command=ShowHourlyMap, bg="#ffeeba").pack(fill="x", pady=2)

# Frame per flights (Dreta)
frame_right = tk.LabelFrame(top_frame, text=" Flight & Arrival Tools ", padx=10, pady=10)
frame_right.pack(side="right", fill="both", expand=True, padx=5)

tk.Button(frame_right, text="Load Arrivals File", command=LoadArrivalsFile).pack(fill="x", pady=2)
tk.Button(frame_right, text="Plot Arrival Frequency", command=PlotArrivalsManual).pack(fill="x", pady=2)
tk.Button(frame_right, text="Plot Flights per Airline", command=PlotAirlinesManual).pack(fill="x", pady=2)
tk.Button(frame_right, text="Plot Schengen Origin Flights", command=PlotTypeManual).pack(fill="x", pady=2)
tk.Button(frame_right, text="Map Flight Trajectories (KML)", command=MapFlightsManual).pack(fill="x", pady=2)
tk.Button(frame_right, text="Check Long Distance Flights", command=CheckLongDistance).pack(fill="x", pady=2)
tk.Button(frame_right, text="Map Long Distance (KML)", command=MapLongDistanceFlightsManual, bg="#e1c9ff").pack(fill="x", pady=2)

# Secció inferior per veure les dades i els GRÀFICS integrats
display_frame = tk.LabelFrame(root, text=" Data & Visual Console ")
display_frame.pack(side="bottom", fill="both", expand=True, padx=15, pady=10)

text = tk.Text(display_frame, height=15, width=45, font=("Courier", 10))
text.pack(side="left", fill="both", expand=True, padx=5, pady=5)

plot_frame = tk.Frame(display_frame, bg="white", bd=1, relief="sunken")
plot_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)


# Carrega automaticament al començar els files
LoadAirportsAuto()
LoadArrivalsAuto()
LoadDeparturesAuto()
LoadLeblStructureAuto()
# ----------------------------------------------------


def OnClosing():
    plt.close('all')
    root.quit()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", OnClosing)

root.mainloop()