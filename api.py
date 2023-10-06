import requests
from bs4 import BeautifulSoup
import json
import os

from planet import PlanetData

# URL of the NASA Planetary Fact Sheet
url = "https://nssdc.gsfc.nasa.gov/planetary/factsheet/"


# store web scraping results in .json
def write_to_json(planet_name, data):
    if os.path.exists("planet_data.json"):
        with open("planet_data.json", "r") as json_file:
            json_data = json.load(json_file)
    else:
        json_data = {}

    json_data[planet_name] = {
        "mass": data[0],
        "diameter": data[1].replace(",", ""),
        "density": data[2],
        "gravity": data[3],
        "rotation_period": data[5],
        "day_length": data[6],
        "orbital_period": data[10].replace(",", ""),
        "orbital_velocity": data[11],
        "mean_temp": data[15]
    }
    
    with open("planet_data.json", "w") as json_file:
        json.dump(json_data, json_file, indent=4)
        
    print("Data successfully saved to planet_data.json")


def get_planet_data(test):
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        table = soup.find("table")

        planet_data = {}

        header = table.find('tr')
        planets = header.find_all('td')[1:]

        for planet_index, planet in enumerate(planets):
            planet_name = planet.text.strip().lower()
            # skip moon
            if planet_name == "moon":
                continue

            data = []
            for row in table.find_all("tr")[1:]:
                columns = row.find_all("td")
                attr = columns[planet_index + 1].text.strip()
                data.append(attr)

            # flag to write data to json for testing
            if test:
                if planet_index < len(planets):
                    write_to_json(planet_name, data)
                else:
                    return None

            planet_data[planet_name] = PlanetData(
                mass = float(data[0]) * 10 **24,
                diameter = float(data[1].replace(",", "")),
                density = float(data[2]),
                gravity = float(data[3]),
                rotation_period = float(data[5]),
                day_length = float(data[6]),
                orbital_period = float(data[10].replace(",", "")),
                orbital_velocity = float(data[11]),
                mean_temp = float(data[15])
            )

        return planet_data

    else:
        print(f"Failed to retrieve data, status code: {response.status_code}")
        return None


if __name__ == "__main__":
    get_planet_data(test=True)
