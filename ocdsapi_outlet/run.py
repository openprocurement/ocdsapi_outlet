import click
import logging
import sys
from zc.lockfile import LockError
from zope.dottedname.resolve import resolve
from ocdsapi.storage import ReleaseStorage
from .utils import interlock, setup_logger


LOGGER = logging.getLogger('ocdsapi.outlet.dumptool')


@click.group()
@click.option('--db-url', help="Couchdb server url", required=True)
@click.option('--db-name', help='Database name', required=True)
@click.option('--lockfile', help='Full path to lockfile', required=True)
@click.option('--log-level', help="Logging level", default='INFO')
@click.option(
    '--log-class',
    help="Logger handler class",
    default="logging.StreamHandler"
    )
@click.option(
    '--log-format',
    help="Logger line formatter",
    default="'%(asctime)s - %(name)s - %(levelname)s - %(message)s'"
    )
@click.option('--log-filename', help='Path to logfile')
@click.pass_context
def cli(
        ctx,
        db_url,
        db_name,
        lockfile,
        log_level,
        log_class,
        log_format,
        log_filename
    ):
    try:
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

        ctx.obj['storage'] = ReleaseStorage(db_url, db_name)
        ctx.obj['lockfile'] = lockfile
    except LockError:
        LOGGER.info("Already running")
