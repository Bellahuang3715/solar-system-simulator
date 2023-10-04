import requests
from bs4 import BeautifulSoup
import json

# URL of the NASA Planetary Fact Sheet
url = "https://nssdc.gsfc.nasa.gov/planetary/factsheet/"

response = requests.get(url)

if response.status_code == 200:
    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find("table")
    planet_data = {}

    header = table.find('tr')
    planets = header.find_all('td')[1:]

    index = 1

    for planet in planets:
        planet_name = planet.text.strip()

        data = []
        for row in table.find_all("tr")[1:]:
            columns = row.find_all("td")
            attr = columns[index].text.strip()
            data.append(attr)
        index = index + 1

        planet_data[planet_name] = {
            "mass": data[0],
            "diameter": data[1],
            "density": data[2],
        }

    with open("planet_data.json", "w") as json_file:
        json.dump(planet_data, json_file, indent=4)

    print("Data successfully saved to planet_data.json")

else:
    print(f"Failed to retrieve data with status code: {response.status_code}")
