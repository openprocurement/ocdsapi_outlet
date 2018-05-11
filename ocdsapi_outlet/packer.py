import requests
from gevent import pool
from urllib.parse import urljoin


DEFAULTS = {
    'pool_size': 25,
}
