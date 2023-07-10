import pytest


@pytest.fixture()
def signup_url_path() -> str:
    return '/api/signup'


@pytest.fixture()
def login_url_path() -> str:
    return '/api/login'


@pytest.fixture()
def logout_url_path() -> str:
    return '/api/logout'


@pytest.fixture()
def posts_url_path() -> str:
    return '/api/posts'
