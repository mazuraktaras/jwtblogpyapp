import pytest


@pytest.fixture()
def user_credentials() -> dict:
    return {
        "username": "username@mtv.tv",
        "password": "password"
    }


@pytest.fixture()
def user_credentials_wrong_username() -> dict:
    return {
        "username": "sername@mtv.tv",
        "password": "password"
    }


@pytest.fixture()
def user_credentials_wrong_password() -> dict:
    return {
        "username": "username@mtv.tv",
        "password": "pasword"  # NOSONAR
    }


@pytest.fixture()
def user_expired_token() -> dict:
    return {
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTY4MDQ1MTAwNCwianRpIjoiM2YwYzk1Y2UtMWY4OS00YTIwLTgyNTUtZGY5YmJlOWU5ODBhIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6InVzZXJuYW1lQG10di50diIsIm5iZiI6MTY4MDQ1MTAwNCwiZXhwIjoxNjgwNDUxMDQwfQ.sDFk5pOsByu5dLHU-eHgPSDsunEfGDTKdE2k7-F9TFY"
    }
