from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
import connections
from config import get_db_config


def main():
    conn = psycopg2.connect(**get_db_config())
    create_table(conn)
    #insert_data(conn)
    conn.close()


def create_table(conn):
    sql_create_table = """
        CREATE TABLE journeys_te (
        id SERIAL PRIMARY KEY,
        source TEXT,
        destination TEXT,
        departure_datetime TIMESTAMP,
        arrival_datetime TIMESTAMP,
        carrier TEXT,
        vehicle_type TEXT,
        price FLOAT,
        currency VARCHAR(3)
    );
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(sql_create_table)
        conn.commit()


def insert_data(conn):
    sql_insert = """
        INSERT INTO journeys_te (source, destination, departure_datetime, arrival_datetime, carrier,
                                vehicle_type, price, currency)
        VALUES (%(source)s,
                %(destination)s,
                %(departure_datetime)s,
                %(arrival_datetime)s,
                %(carrier)s,
                %(vehicle_type)s,
                %(price)s,
                %(currency)s);
    """
    journeys = get_data()
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        for journey in journeys:
            cursor.execute(sql_insert, journey)
        conn.commit()


def get_data():
    journeys = connections.get_connections_interval('brno', 'praha', '2018-12-17', '2018-12-19')
    journeys = [enrich(journey) for journey in journeys]
    return journeys


def enrich(journey):
    return {
        'source': journey['source'],
        'destination': journey['destination'],
        'departure_datetime': to_datetime(journey['date'], journey['departure']),
        'arrival_datetime': to_datetime(journey['date'], journey['arrival']),
        'carrier': 'euroline',
        'vehicle_type': 'bus',
        'price': journey['price'],
        'currency': 'EUR'
    }


def to_datetime(date, time):
    return datetime.strptime(f'{date} {time}', '%Y-%m-%d %H:%M')


if __name__ == "__main__":
    main()
