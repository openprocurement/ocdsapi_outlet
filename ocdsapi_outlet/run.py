""" run.py - main module """

from gevent import monkey
monkey.patch_all()

import click
import logging
from datetime import datetime
import sys
import yaml
import json
import os.path
#from zc.lockfile import LockError
from zope.dottedname.resolve import resolve
from ocdsapi.storage import ReleaseStorage
from .utils import setup_logger
from .manifest import Manifest


LOGGER = logging.getLogger('ocdsapi.outlet.dumptool')
DEFAULT_RENDERER = 'json'


@click.group()
@click.option('--db-url', help="Couchdb server url", required=True)
@click.option('--db-name', help='Database name', required=True)
@click.option('--package-meta', help="Path to releases metainfo", required=True)
@click.option('--renderer', help="JSON renderer to use", required=False, default=DEFAULT_RENDERER)
@click.option(
    '--with-zip',
    help="Create zip archive with all packages",
    required=False, default=True
)
@click.option(
    '--count',
    help='Count of releases in package',
    type=int,
    default=2048
)
@click.option(
    '--clean-up',
    help='Clean up raw json after creating zip file',
    type=bool,
    default=False
)
@click.option('--log-level', help="Logging level", default='INFO')
@click.option(
    '--log-class',
    help="Logger handler class",
    default="logging.StreamHandler"
    )
@click.option(
    '--log-format',
    help="Logger line formatter",
    default="%(asctime)s - [%(name)s - %(levelname)s] - %(message)s"
    )
@click.option('--log-filename', help='Path to logfile')
@click.pass_context
def cli(ctx,
        db_url,
        db_name,
        package_meta,
        renderer,
        with_zip,
        count,
        clean_up,
        log_level,
        log_class,
        log_format,
        log_filename):
    if not ctx.obj:
        ctx.obj = {}
    try:
        handler = resolve(log_class)
    except ImportError:
        click.echo("Invalid logging class. Failing back to default")
        from logging import StreamHandler
        handler = StreamHandler
        log_filename = sys.stdout

    ctx.obj['logger'] = setup_logger(
       LOGGER,
       handler,
       log_level,
       log_format,
       log_filename
    )
    try:
        renderer_class = resolve(renderer)
        if not all((hasattr(renderer_class, r) for r in ('load', 'dump'))):
            raise Exception
    except (ImportError, Exception) as error:
        LOGGER.warn(
            "Invalid renderer {}. Reason {}. "
            "Going back to default.".format(
                renderer,
                error
            ))
        renderer_class = resolve(DEFAULT_RENDERER)
    if not db_url.startswith('http'):
        db_url = 'http://{}'.format(db_url)
    ctx.obj['storage'] = ReleaseStorage(db_url, db_name)
    ctx.obj['package_capacity'] = count
    ctx.obj['renderer'] = renderer_class
    ctx.obj['with_zip'] = with_zip
    ctx.obj['key_prefix'] = "merged-{}".format(datetime.now().strftime("%Y-%m-%d"))
    ctx.obj['manifest'] = Manifest()
    ctx.obj['clean_up'] = clean_up
    if package_meta.endswith('yaml') or package_meta.endswith('yml'):
        load = yaml.load
    elif package_meta.endswith('json'):
        load = json.load
    else:
        LOGGER.fatal("Invalid filetype with metainfo")
        sys.exit(2)
    try:
        with open(os.path.abspath(package_meta)) as _meta:
            ctx.obj['metainfo'] = load(_meta)
    except IOError as this_error:
        LOGGER.error("Provided file {} does not exists. Error: {}".format(package_meta, this_error))
