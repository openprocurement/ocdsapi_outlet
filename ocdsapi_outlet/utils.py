""" utils.py - helper functions """

import logging
import functools
import operator
from repoze.lru import lru_cache
try:
    import boto3
except ImportError:
    boto3 = None


def setup_logger(
        logger,
        handler,
        level,
        formatter,
        filename):
    if filename:
        handler = functools.partial(handler, filename)
    handler = handler()
    if formatter:
        handler.setFormatter(logging.Formatter(formatter))
    logger.addHandler(handler)
    logger.setLevel(getattr(logging, level.upper()))
    return logger


def find_package_date(releases):
    """ Find max date inside package """
    return max(
        releases,
        key=operator.itemgetter('date')
        ).get('date')


def prepare_package(date, metainfo=None):
    """ Prepare metainfo for package """
    base = {
        'publishedDate': date,
        'releases': [],
        'publisher': {
            'name': '',
            'scheme': '',
            'uri': ''
        },
        'lisence': ''
    }
    if metainfo:
        base.update(metainfo)
    return base


@lru_cache(maxsize=1)
def connect_bucket(cfg):
    """ TODO: do we really need this? """
    return (
        cfg['bucket'],
        boto3.client('s3')
        )
