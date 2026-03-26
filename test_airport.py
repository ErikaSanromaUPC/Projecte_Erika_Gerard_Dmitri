from airport import (Airport, SetSchengen, PrintAirport,
                     AddAirport, RemoveAirport, SaveSchengenAirports, LoadAirports,PlotAirports,MapAirports)
from aircraft import (PlotArrivals,LoadArrivals)

print("=" * 50)
print("TEST 1: Airport() and PrintAirport()")
print("=" * 50)
airport1 = Airport("LEBL", 41.297445, 2.0832941)
SetSchengen(airport1)
PrintAirport(airport1)

print("-" * 20)
airport2 = Airport("EGLL", 51.4775, -0.4614)
SetSchengen(airport2)
PrintAirport(airport2)

print()
airport3 = Airport("KJFK", 40.6413, -73.7781)
SetSchengen(airport3)
PrintAirport(airport3)

print("=" * 50)
print("TEST 2: Provar funcions LoadAirports, SaveSchengenAirports, AddAirports, RemoveAirports")
print("=" * 50)

test_airport = LoadAirports("Airports.txt")
#Provar AddAirport
new_airport = Airport("EDDB", 52.3667, 13.5033)
if AddAirport(test_airport, new_airport):
    print("Airport EDDB added succesfully.")
#Provar RemoveAirport
return_test_remove_airport1 = RemoveAirport(test_airport, "CAAA")
if return_test_remove_airport1 == 0:  # Comprobamos la variable del resultado, no la lista
    print("Airport CAAA removed successfully.")
else:
    print("Error: Airport CAAA couldn't be removed.")

# --- Provar RemoveAirport para LEBL ---
return_test_remove_airport2 = RemoveAirport(test_airport, "LEBL")
if return_test_remove_airport2 == 0:
    print("Airport LEBL removed successfully.")
else:
    print("Error: Airport LEBL couldn't be removed.")
#Provar SaveSchengenAirports
test_schengen_saved= SaveSchengenAirports(test_airport, "testSchengen.txt")
print(f"{test_schengen_saved} airports Schengen saved.")


print("=" * 50)
print("TEST 2: Plot and Map")
print("=" * 50)

# Genera el gràfic
print("Generating plot")
PlotAirports(test_airport)

# Genera arxiu kml
kml_file = MapAirports(test_airport, "my_airports.kml")
print(f"kml file generated {kml_file}. You can open it with google earth.")
#Final

print("=" * 50)
print("ALL TESTS COMPLETED")
print("=" * 50)

#----
test_aircraft = LoadArrivals("Arrivals.txt")
print("Generating plot 2")
PlotArrivals(test_aircraft)
