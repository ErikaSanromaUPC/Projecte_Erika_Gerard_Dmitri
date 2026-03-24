import tkinter as tk
from tkinter import filedialog, messagebox
from airport import *

airports = []

def load_airports():
    filename = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    if filename:
        global airports
        airports = LoadAirports(filename)
        show_airports()

def save_schengen():
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

def add_airport():
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

def remove_airport():
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
    messagebox.showinfo("Map Generated", f"The file {filename} has been created.\nOpen it with Google Earth.")

def show_airports():
    text.delete("1.0", tk.END) #Aicò borra tot, perquè no s'apilin els aeroports carregats
    if not airports:
        text.insert(tk.END, "No airports loaded.")
        return
    i=0
    while i < len(airports):
        airport = airports[i]
        # Utilitzem :.4f per posar 4 decimals
        text.insert(tk.END,f"{airport.code:6} | Lat: {airport.latitude:>8.4f} | Lon: {airport.longitude:>8.4f} | Schengen: {airport.schengen}\n") #Es veu amb moltes coses perquè està posat amb un format bonic
        i+=1
root = tk.Tk()
root.title("Airport Manager v1 (Erika, Gerard, Dmitri)")

# Botons
tk.Button(root, text="Load Airports", command=load_airports).pack(fill="x")
tk.Button(root, text="Save Schengen Airports", command=save_schengen).pack(fill="x")
tk.Button(root, text="Plot Airports", command=plot_airports).pack(fill="x")
tk.Button(root, text="Map Airports", command=map_airports).pack(fill="x")

# Textboxs per posar informació
tk.Label(root, text="Code:").pack()
code_entry = tk.Entry(root)
code_entry.pack()

tk.Label(root, text="Latitude:").pack()
lat_entry = tk.Entry(root)
lat_entry.pack()

tk.Label(root, text="Longitude:").pack()
lon_entry = tk.Entry(root)
lon_entry.pack()

# Botons per afegir i eliminar aeroports
tk.Button(root, text="Add Airport", command=add_airport).pack(fill="x")
tk.Button(root, text="Remove Airport", command=remove_airport).pack(fill="x")

# Àrea del text perquè quedi més bonic
text = tk.Text(root, height=20, width=60)
text.pack()

root.mainloop()
