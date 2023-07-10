from os import getenv

# ----- App configuration section -----
PREFERRED_URL_SCHEME = 'http'

SECRET_KEY = getenv("SECRET_KEY")
SQLALCHEMY_DATABASE_URI = getenv("DATABASE_URI")
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
SQLALCHEMY_ECHO = False
JWT_SECRET_KEY = getenv("JWT_SECRET_KEY")
JWT_BLACKLIST_ENABLED = True
JWT_BLACKLIST_TOKEN_CHECKS = ['access']
JWT_TOKEN_LOCATION = ['headers', 'cookies', 'json']
JWT_COOKIE_CSRF_PROTECT = False
JWT_CSRF_CHECK_FORM = False
JWT_ACCESS_TOKEN_EXPIRES = 3600
PROPAGATE_EXCEPTIONS = True

API_URL = f'http://127.0.0.1:{getenv("APP_PORT", default="8080")}'

# ----- Blog Bot configuration section -----
BOT_NUMBER_OF_USERS = 3
BOT_MAX_POSTS_PER_USER = 1
BOT_MAX_LIKES_PER_USER = 20
