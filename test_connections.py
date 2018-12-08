import connections


def test_normalize():
    assert connections.normalize(') Hradec Králové ') == 'hradeckralove'
