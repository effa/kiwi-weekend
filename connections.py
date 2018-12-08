"""
Example usage:
$ pipenv run python connections.py --source Brno --destination Praha --departure_date 2018-12-09
"""
import argparse
import json
import re
from requests_html import HTMLSession
from unidecode import unidecode


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source')
    parser.add_argument('--destination')
    parser.add_argument('--departure_date')
    args = parser.parse_args()
    connections_data = get_connections(args.source, args.destination, args.departure_date)
    print(connections_data)


def get_connections(source, destination, departure_date):
    codes_map = get_city_codes()
    rates = get_rates()
    source = get_city_code(source, codes_map)
    destination = get_city_code(destination, codes_map)
    # The URL is e.g. 'https://www.elines.cz/jizdenky?from=CZE%7EBrno&to=CZE%7EPrague&forth=2018-12-09&back='
    url = f'https://www.elines.cz/jizdenky?from={source}&to={destination}&forth={departure_date}&back='
    session = HTMLSession()
    response = session.get(url)
    connections_list = response.html.find(f'.day-1[data-date="{departure_date}"]')
    return [parse_connection_element(el, rates) for el in connections_list]


def get_city_codes():
    session = HTMLSession()
    response = session.get('https://elines.cz/cz/')
    cities_elements = response.html.find('#cities option')
    codes_map = {}
    for city_element in cities_elements:
        code = city_element.attrs['value']
        names = city_element.text
        if '~' in code:
            for name in names.split('('):
                codes_map[normalize(name)] = code
    return codes_map


def normalize(name):
    name= unidecode(name)
    name = re.sub(r'\W+', '', name)
    name = name.lower()
    return name


def get_city_code(city_name, codes_map):
    return codes_map[normalize(city_name)]


def parse_connection_element(connection_element, rates):
    departure = connection_element.find('section.departure > span')[0].text
    arrival = connection_element.find('section.arrival > span')[0].text
    price_czk = float(connection_element.find('section.price .basic .amount')[0].text)
    price = czk_to_eur(price_czk, rates)
    return {'departure': departure, 'arrival': arrival, 'price': price}


def get_rates():
    session = HTMLSession()
    response = session.get('https://api.skypicker.com/rates')
    return response.json()


def czk_to_eur(czk, rates):
    return rates['CZK'] * czk


if __name__ == "__main__":
    main()
