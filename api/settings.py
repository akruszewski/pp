import os

TEMPERATURE_API_URL = os.environ.get(
    'TEMPERATURE_API_URL',
    'http://localhost:8000/'
)
WINDSPEED_API_URL = os.environ.get(
    'WINDSPEED_API_URL',
    'http://localhost:8080/'
)
DEBUG = os.environ.get(
    'API_DEBUG',
    False
)
HOST = os.environ.get(
    'API_HOST',
    'localhost'
)
PORT = os.environ.get(
    'API_PORT',
    8000
)


# gunicorn configuration

bind = f"{HOST}:{PORT}"
workers = os.environ.get(
    'API_WORKERS',
    1
)
