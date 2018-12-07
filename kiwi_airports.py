import argparse
import json
import requests


def print_airports(names=True, iata=True, cities=False, coords=False):
    url = (
        "https://api.skypicker.com/locations?"
        "type=subentity&term=GB&active_only=true&location_types=airport"
    )
    data = requests.get(url).json()["locations"]
    airports = []
    for d in data:
        airport = {}
        if names:
            airport["name"] = d["name"]
        if iata:
            airport["IATA"] = d["code"]
        if cities:
            airport["city"] = d["city"]["name"]
        if coords:
            airport["location"] = d["location"]
        airports.append(airport)
    if sum([names, iata, cities, coords]) == 1:
        airports = [list(airport.values())[0] for airport in airports]
        if not coords:
            airports = sorted(set(airports))
    print(json.dumps(airports, indent=1))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--names",
        action="store_true",
        default=False,
        help="Include names of the airports.",
    )
    parser.add_argument(
        "--iata",
        action="store_true",
        default=False,
        help="Include IATA codes of the airports.",
    )
    parser.add_argument(
        "--cities", action="store_true", default=False, help="Include cities."
    )
    parser.add_argument(
        "--coords", action="store_true", default=False, help="Include coordinates."
    )
    parser.add_argument(
        "--full",
        action="store_true",
        default=False,
        help="Include all information about airports.",
    )
    args = parser.parse_args()
    if args.full:
        args.names = args.iata = args.cities = args.coords = True
    if not any([args.names, args.iata, args.cities, args.coords]):
        args.names = args.iata = True
    print_airports(
        names=args.names, iata=args.iata, cities=args.cities, coords=args.coords
    )


if __name__ == "__main__":
    main()
