"""
Example usage:
$ pipenv run python connections.py --source Brno --destination Praha --departure_date 2018-12-09
"""
import argparse
import json
import re
from redis import StrictRedis
from requests_html import HTMLSession
from unidecode import unidecode


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source')
    parser.add_argument('--destination')
    parser.add_argument('--departure_date')
    args = parser.parse_args()
    connections_data = get_connections(args.source, args.destination, args.departure_date)
    print(json.dumps(connections_data))


def get_connections(source, destination, departure_date, session=None):
    session = session or HTMLSession()
    redis = StrictRedis(socket_connect_timeout=3, **get_redis_config())
    rates = get_rates(session)
    source = normalize(source)
    destination = normalize(destination)
    source_code = get_city_code(source, redis, session)
    destination_code = get_city_code(destination, redis, session)
    journey_key = get_redis_journey_key(source, destination, departure_date)
    journeys = redis.get(journey_key)
    if journeys:
        print('Using cached journeys...')
        return json.loads(journeys.decode('utf-8'))
    print('Scraping journeys...')
    # The URL is e.g. 'https://www.elines.cz/jizdenky?from=CZE%7EBrno&to=CZE%7EPrague&forth=2018-12-09&back='
    url = f'https://www.elines.cz/jizdenky?from={source_code}&to={destination_code}&forth={departure_date}&back='
    response = session.get(url)
    connection_elements = response.html.find(f'.day-1[data-date="{departure_date}"]')
    connections = [parse_connection_element(el, rates) for el in connection_elements]
    redis.setex(journey_key, 60*60, json.dumps(connections))
    return connections


def get_and_cache_city_codes(session, redis):
    print('Scraping city codes...')
    response = session.get('https://elines.cz/cz/')
    cities_elements = response.html.find('#cities option')
    codes_map = {}
    for city_element in cities_elements:
        code = city_element.attrs['value']
        names = city_element.text
        if '~' in code:
            for name in names.split('('):
                codes_map[normalize(name)] = code
    for city_name, code in codes_map.items():
        city_key = get_redis_location_key(city_name)
        redis.setex(city_key, 60*60, code)
    return codes_map


def normalize(name):
    name= unidecode(name)
    name = re.sub(r'\W+', '', name)
    name = name.lower()
    return name


def get_city_code(city_name, redis, session):
    city_name = normalize(city_name)
    city_code = redis.get(get_redis_location_key(city_name))
    if city_code:
        return city_code.decode('utf-8')
    codes_map = get_and_cache_city_codes(session, redis)
    return codes_map[normalize(city_name)]


def get_redis_location_key(city_name):
    return f'location:{city_name}_eurolines'


def get_redis_journey_key(source, destination, departure_date):
    return f'journey:{source}_{destination}_{departure_date}_eurolines'

def parse_connection_element(connection_element, rates):
    departure = connection_element.find('section.departure > span')[0].text
    arrival = connection_element.find('section.arrival > span')[0].text
    price_czk = min(float(el.text) for el in connection_element.find('section.price .amount'))
    price = czk_to_eur(price_czk, rates)
    return {'departure': departure, 'arrival': arrival, 'price': price}


def get_rates(session):
    response = session.get('https://api.skypicker.com/rates')
    return response.json()


def czk_to_eur(czk, rates):
    return rates['CZK'] * czk


def get_redis_config():
    return {
        'host': '142.93.160.67',
        'password': 'akd89DSk23Kldl0ram29',
        'port': 6379,
    }




if __name__ == "__main__":
    main()
