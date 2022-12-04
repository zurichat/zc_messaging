from decouple import config

BASE_URL = 'https://api.novu.co/v1'

# declare NOVU_API_KEY in .env file
# example:
# NOVU_API_KEY = acc7708b8e05bc3f7d61dd629d320b41


FULL_HEADER = {
    'Authorization': 'ApiKey '+config('NOVU_API_KEY'),
    'Content_Type': 'application/json'
}

# simple header with just Api_key
SMALL_HEADER = {'Authorization': 'ApiKey ' +
                config('NOVU_API_KEY', '')}


class Core:

    """
    Generic configurations for all NovuPy modules can all be edited from here
    """

    def __init__(self) -> None:

        self.base_url = BASE_URL

        self.s_header = SMALL_HEADER

        self.headers = FULL_HEADER


core = Core()
