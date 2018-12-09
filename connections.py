"""
Example usage:
$ pipenv run python connections.py --source Brno --destination Praha --departure_date 2018-12-09
"""
import argparse
from datetime import datetime, timedelta
import json
import re
from redis import StrictRedis
from requests_html import HTMLSession
from unidecode import unidecode
import config


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source')
    parser.add_argument('--destination')
    parser.add_argument('--departure_date')
    parser.add_argument('--date_from')
    parser.add_argument('--date_to')
    args = parser.parse_args()
    if args.date_from and args.date_to:
        connections_data = get_connections_interval(args.source, args.destination, args.date_from, args.date_to)
    else:
        connections_data = get_connections(args.source, args.destination, args.departure_date)
    print(json.dumps(connections_data))


def get_connections_interval(source, destination, date_from, date_to):
    # TODO: Factor out common logic from this and get_connectoins.
    # (The easies option is to just call get_connections_interval from
    # get_connections).
    session = HTMLSession()
    redis = StrictRedis(socket_connect_timeout=3, **config.get_redis_config())
    rates = get_rates(session)
    source = normalize(source)
    destination = normalize(destination)
    source_code = get_city_code(source, redis, session)
    destination_code = get_city_code(destination, redis, session)
    date_from = datetime.strptime(date_from, '%Y-%m-%d')
    date_to = datetime.strptime(date_to, '%Y-%m-%d')
    dates = [
        (date_from + timedelta(i)).date()
        for i in range((date_to-date_from).days + 1)]
    journey_keys = [
        get_redis_journey_key(source, destination, date)
        for date in dates]
    pipe = redis.pipeline()
    for journey_key in journey_keys:
        pipe.get(journey_key)
    cached_journeys = pipe.execute()
    all_journeys = []
    for date, journey_key, cached_journey in zip(dates, journey_keys, cached_journeys):
        if cached_journey:
            all_journeys.extend(json.loads(cached_journey.decode('utf-8')))
        else:
            date_string = date.strftime('%Y-%m-%d')
            print(f'Scraping journeys for {date_string}...')
            # The URL is e.g. 'https://www.elines.cz/jizdenky?from=CZE%7EBrno&to=CZE%7EPrague&forth=2018-12-09&back='
            url = f'https://www.elines.cz/jizdenky?from={source_code}&to={destination_code}&forth={date_string}&back='
            response = session.get(url)
            connection_elements = response.html.find(f'.day-1[data-date="{date_string}"]')
            connections = [parse_connection_element(el, date_string, rates) for el in connection_elements]
            redis.setex(journey_key, 60*60, json.dumps(connections))
            all_journeys.extend(connections)
    return all_journeys


def get_connections(source, destination, departure_date, session=None):
    session = session or HTMLSession()
    redis = StrictRedis(socket_connect_timeout=3, **config.get_redis_config())
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
    connections = [parse_connection_element(el, departure_date, rates) for el in connection_elements]
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

def parse_connection_element(connection_element, date, rates):
    departure = connection_element.find('section.departure > span')[0].text
    arrival = connection_element.find('section.arrival > span')[0].text
    price_czk = min(float(el.text) for el in connection_element.find('section.price .amount'))
    price = czk_to_eur(price_czk, rates)
    return {'date': date, 'departure': departure, 'arrival': arrival, 'price': price}


def get_rates(session):
    response = session.get('https://api.skypicker.com/rates')
    return response.json()


def czk_to_eur(czk, rates):
    return rates['CZK'] * czk


if __name__ == "__main__":
    main()
