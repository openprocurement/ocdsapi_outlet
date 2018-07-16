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
    }
    if metainfo:
        base.update(metainfo)
    return base


@lru_cache(maxsize=1)
def connect_bucket(cfg):
    """ TODO: do we really need this? """
    return (
        cfg.bucket,
        boto3.client('s3')
        )


def prepare_pack_command(cfg):
    base_bin = cfg.get('bin_path', 'ocds-pack')
    base_args = [
        base_bin,
        '--package-meta',
        cfg.get('dump', {}).get('metainfo_file', 'meta.yml')
    ]
    for key in ('clean_up', 'with_zip', 'count'):
        if cfg.get('dump', {}).get(key):
            base_args.extend([
                '--{}'.format(key.replace('_', '-')),
                str(cfg['dump'][key])
            ])

    db_args = [
        item
        for arg, value in cfg.get('db').items()
        for item in '--{} {}'.format(arg.replace('_', '-'), value).split()
    ]

    backend = list(cfg.get('backend', {'fs': ''}).keys())[0]
    backend_args = [backend]
    backend_args.extend([
        item
        for arg, value in cfg['backend'][backend].items()
        for item in '--{} {}'.format(arg.replace('_', '-'), value).split()
    ])
    for args in db_args, backend_args:
        base_args.extend(args)
    return base_args
