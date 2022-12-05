import os

from decouple import config

"""
install python-decouple and add the environment variables in a .env file to run locally

in Production, create BASE_URL & NOVU_API_KEY with their respective values
"""

DEFAULT_BASE_URL = 'http://139.144.17.179:3000/'
DEFAULT_API_KEY = '1c7cd3cffa34acf1a99bf642368fab78'

BASE_URL = os.environ.get('BASE_URL', config(
    'BASE_URL', default=DEFAULT_BASE_URL))

NOVU_API_KEY = os.environ.get('NOVU_API_KEY', config(
    'NOVU_API_KEY', default=DEFAULT_API_KEY))

FULL_HEADER = {
    'Authorization': 'ApiKey ' + NOVU_API_KEY,
    'Content_Type': 'application/json'
}

# simple header with just Api_key
SMALL_HEADER = {'Authorization': 'ApiKey ' + NOVU_API_KEY}


class Core:

    """
    Generic configurations for all NovuPy modules can all be edited from here
    """

    def __init__(self) -> None:

        self.base_url = BASE_URL

        self.s_header = SMALL_HEADER

        self.headers = FULL_HEADER


core = Core()