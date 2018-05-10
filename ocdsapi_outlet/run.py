import click
import logging
from zc.lockfile import LockError
from ocdsapi.storage import ReleaseStorage
from .utils import interlock
from .backedns import backend


LOGGER = logging.getLogger('ocdsapi.outlet.dumptool')


@click.group()
@click.option('--db-url', help="Couchdb server url", required=True)
@click.option('--db-name', help='Database name', required=True)
@click.option('--lockfile', help='Full path to lockfile', required=True)
@click.option('--api-url', help='API url', required=True)
@click.pass_context
def cli(ctx, db_url, db_name, lockfile, api_url):
    try:
        with interlock(lockfile) as lock:
            ctx.obj['storage'] = ReleaseStorage(db_url, db_name)
            ctx.obj['lock'] = lock
            ctx.obj['api_url'] = api_url
    except LockError:
        LOGGER.info("Already running")
