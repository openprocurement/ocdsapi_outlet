import os
import os.path
import logging
import click
from .base import BaseOutlet, BaseHandler
from ..run import cli
from ..dumptool import OCDSPacker


LOGGER = logging.getLogger('ocdsapi.outlet.dumptool')
DEFAULT_RENDERER = 'json'


class FileHandler(BaseHandler):

    def __init__(self, cfg, renderer, meta):
        super().__init__(cfg, renderer, meta)

        self.destination = cfg.get('file_path')
        if not os.path.exists(self.destination):
            os.makedirs(self.destination)
        self.name = '{}.json'.format(self.meta['date'])

    def write_releases(self, releases):
        self.meta['releases'] = releases
        try:
            with open(os.path.join(self.destination, self.name), 'w') as f:
                self.renderer.dump(self.meta, f)
            LOGGER.info('Done package {}'.format(self.meta['date']))
        except Exception as e:
            LOGGER.fatal("Error writing release. error: {}".format(e))
        finally:
            del self.meta['releases']


class FSOutlet(BaseOutlet):

    def __init__(self, cfg, renderer, with_zip):
        super().__init__(FileHandler, cfg, renderer, with_zip)


@click.command(name='fs')
@click.option(
    '--file-path',
    help="Destination path to store static dump",
    required=True
    )
@click.option(
    '--renderer',
    help='Python library to serialize jsons',
    default='simplejson'
    )
@click.option(
    '--with-zip',
    help="Flag to create zip archive with all releases",
    default=False
)
@click.pass_context
def fs(ctx, **kw):
    logger = ctx.obj['logger']
    storage = ctx.obj['storage']
    count = ctx.obj['count']
    logger.info("Start packing")

    renderer = kw.pop('renderer')
    with_zip = kw.pop('with_zip')
    packer = OCDSPacker(
        storage,
        FSOutlet(kw, renderer, with_zip),
        pack_count=count
        )
    packer.packdb()
