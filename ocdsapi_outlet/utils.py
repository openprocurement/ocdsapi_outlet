import logging
import functools
import operator
import os.path
from repoze.lru import lru_cache
try:
    import boto3
except ImportError:
    boto3 = None


DEFATULT_PATHS = [
    '.',
    'bin',
]


def setup_logger(
    logger,
    handler,
    level,
    formatter,
    filename
    ):
    
    if filename:
        handler = functools.partial(handler, filename)
    handler = handler()
    if formatter:
        handler.setFormatter(logging.Formatter(formatter))
    logger.addHandler(handler)
    logger.setLevel(getattr(logging, level.upper()))
    return logger


def find_package_date(releases):
    return max(
        releases,
        key=operator.itemgetter('date')
        ).get('date')


def prepare_package(date):
    return {
        'date': date,
        'releases': [],
        'publisher': {
            'name': '',
            'scheme': '',
            'uri': ''
        },
        'lisence': ''
    }


@lru_cache(maxsize=1)
def connect_bucket(cfg):
    return (
        cfg['bucket'],
        boto3.client('s3')
        )