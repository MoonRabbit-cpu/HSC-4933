import requests

YEAR = 2020
DATASET = "dec/pl"

URL = f"https://api.census.gov/data/{YEAR}/{DATASET}"
API_KEY = "3a82b48e545eb9b64cf24c657a735c96a7708759"

params = {
    "get": "NAME,P1_001N",
    "for": "state:*",
    "key": API_KEY,
}

response = requests.get(URL, params=params)
response.raise_for_status()
data = response.json()



print(f"Got {len(data) - 1} rows back")

for i in data:
    print(i)

