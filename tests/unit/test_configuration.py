from jwtblogapp import config, app

client = app.test_client()


def test_application_port_is_8080():
    assert '8080' in config.API_URL


def test_if_security_key():
    assert config.SECRET_KEY


def test_client():
    result = client.get('/')
    assert '2021' in result.text
