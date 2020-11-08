import pandas as pd
import aux
import logging

domain = "https://www.pisos.com"
path = "/venta/pisos-barcelona/"

# Get all the cities from the pisos.com browser
cities = aux.getCitiesToScan(domain, path)

list_cities = []

# Find all options in the brower for each page and build the cities list
# (depending on the city, the browser changes)
for city in cities:
    new_cities = aux.getCitiesToScan(domain, city)
    for new_city in new_cities:
        # Append to the list if it's not there
        try:
            list_cities.index(new_city)
        except:
            list_cities.append(new_city)

print('Ciudades a buscar: ' + str(len(list_cities)))

pisos = []

# Get all pisos for sale for each city
for city in list_cities:
    pisos = pisos + aux.scanPath(domain, city)
    print(len(pisos))

print('Búsqueda terminada')

# Export to csv
pisos = pd.DataFrame(pisos)
pisos.to_csv('pisos.csv', encoding='utf-8')
