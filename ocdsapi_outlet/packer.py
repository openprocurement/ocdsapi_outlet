import requests
from gevent import pool
from urllib.parse import urljoin


DEFAULTS = {
    'pool_size': 25,
}


class State:

    def __init__(self, api_url, storage):
        self.api_url = api_url
        self.storage = storage
        self.session = requests.Session()

    def run(self):
        state = self._freeze_state()

    def _freeze_state(self):
        pool = pool.Pool(DEFAULTS['pool_size'])
        start_point = self.session.get(
            urljoin(self.api_url, 'releases.json')
        )
        
