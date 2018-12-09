import psycopg2
from psycopg2.extras import RealDictCursor
from config import get_db_config


def find_multijourneys(source, destination, date_from, date_to):
    # TODO: multi-steps journeys
    sql_select = """
        SELECT * FROM journeys_te
        WHERE source = %(source)s
            AND destination = %(destination)s
            AND departure_datetime >= %(date_from)s
            AND departure_datetime <= %(date_to)s
    """
    conn = psycopg2.connect(**get_db_config())
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        params = {
            'source': source,
            'destination': destination,
            'date_from': date_from,
            'date_to': date_to + ' 23:59:59',
        }
        cursor.execute(sql_select, params)
        results = cursor.fetchall()
    conn.close()
    return results
