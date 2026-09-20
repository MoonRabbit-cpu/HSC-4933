import os
import requests

YEAR = 2020
DATASET = "dec/pl"
BASE_URL = f"https://api.census.gov/data/{YEAR}/{DATASET}"

# Prefer an environment variable so the key doesn't live in source code;
# falls back to the key you had hardcoded so this still runs as-is.
API_KEY = os.environ.get("CENSUS_API_KEY", "3a82b48e545eb9b64cf24c657a735c96a7708759")

STATE_FIPS = {
    "alabama": "01", "alaska": "02", "arizona": "04", "arkansas": "05",
    "california": "06", "colorado": "08", "connecticut": "09", "delaware": "10",
    "district of columbia": "11", "florida": "12", "georgia": "13", "hawaii": "15",
    "idaho": "16", "illinois": "17", "indiana": "18", "iowa": "19",
    "kansas": "20", "kentucky": "21", "louisiana": "22", "maine": "23",
    "maryland": "24", "massachusetts": "25", "michigan": "26", "minnesota": "27",
    "mississippi": "28", "missouri": "29", "montana": "30", "nebraska": "31",
    "nevada": "32", "new hampshire": "33", "new jersey": "34", "new mexico": "35",
    "new york": "36", "north carolina": "37", "north dakota": "38", "ohio": "39",
    "oklahoma": "40", "oregon": "41", "pennsylvania": "42", "rhode island": "44",
    "south carolina": "45", "south dakota": "46", "tennessee": "47", "texas": "48",
    "utah": "49", "vermont": "50", "virginia": "51", "washington": "53",
    "west virginia": "54", "wisconsin": "55", "wyoming": "56", "puerto rico": "72",
}


def resolve_state(entry):
    """Accept a state name or FIPS code and return its 2-digit FIPS code."""
    entry = entry.strip()
    if not entry:
        return None
    if entry.isdigit():
        return entry.zfill(2)
    return STATE_FIPS.get(entry.lower())


def get_geography():
    raw = input(
        "Enter state name(s) or FIPS code(s), comma-separated "
        "(e.g. 'Florida, Georgia' or '12,13'), or press Enter for all states: "
    )
    if not raw.strip():
        return "state:*"

    codes = []
    for entry in raw.split(","):
        fips = resolve_state(entry)
        if fips is None:
            print(f"  Warning: could not recognize '{entry.strip()}', skipping.")
        else:
            codes.append(fips)

    if not codes:
        print("No valid states recognized; defaulting to all states.")
        return "state:*"

    return "state:" + ",".join(codes)


def get_variables():
    raw = input(
        "Enter Census variable name(s), comma-separated "
        "(e.g. 'P1_001N,P1_003N'): "
    )
    variables = [v.strip() for v in raw.split(",") if v.strip()]
    if not variables:
        print("No variables entered; defaulting to P1_001N (total population).")
        variables = ["P1_001N"]
    return variables


def main():
    geo_filter = get_geography()
    variables = get_variables()

    params = {
        "get": "NAME," + ",".join(variables),
        "for": geo_filter,
        "key": API_KEY,
    }

    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()
    data = response.json()

    print(f"\nGot {len(data) - 1} rows back\n")
    for row in data:
        print(row)


if __name__ == "__main__":
    main()