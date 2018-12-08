from unittest.mock import MagicMock
from requests_html import HTMLSession
import requests
import connections


def test_normalize():
    assert connections.normalize(') Hradec Králové ') == 'hradeckralove'


#def test_get_connections():
#    session = HTMLSession()
#    def fake_session_get(url):
#        response = requests.Response()
#        if url == 'https://api.skypicker.com/rates':
#            response.json = MagicMock(return_value={"CZK":0.0386738})
#        # TODO: return current content for the 3 urls
#        elif url == 'https://elines.cz/cz/':
#            response._content = 'todo'.encode('utf-8')
#        return response
#    session.get = MagicMock(side_effect=fake_session_get)
#    results = connections.get_connections('Brno', 'Praha', '2018-12-09', session=session)
#    assert results == [{"departure": "13:45", "arrival": "16:15", "price": 8.314867}]
