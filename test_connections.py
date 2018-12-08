from unittest.mock import MagicMock
from requests_html import HTMLSession
import connections


def test_normalize():
    assert connections.normalize(') Hradec Králové ') == 'hradeckralove'


#def test_get_connections():
#    session = HTMLSession()
#    # TODO: return current content for the 3 urls
#    session.get = MagicMock(side_effect=)
#    results = connections.get_connections('Brno', 'Praha', '2018-12-09', session=session)
#    assert results == [{"departure": "13:45", "arrival": "16:15", "price": 8.314867}]
