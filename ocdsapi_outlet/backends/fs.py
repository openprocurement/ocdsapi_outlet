import os
import os.path
import logging
import click
from contextlib import contextmanager
from zope.dottedname.resolve import resolve
from ..run import cli
from ..dumptool import OCDSPacker


LOGGER = logging.getLogger('ocdsapi.outlet.dumptool')
DEFAULT_RENDERER = 'json'


class Handler:

    def __init__(self, meta, handler, renderer):
        self.meta = meta
        self.handler = handler
        self.renderer = renderer

    def write_releases(self, releases):
        self.meta['releases'] = releases
        try:
            self.renderer.dump(self.meta, self.handler)
            LOGGER.info('Done package {}'.format(self.meta['date']))
        except Exception as e:
            LOGGER.fatal("Error wrinting release. error: {}".format(e))
        finally:
            del self.meta


class FSOutlet:

    def __init__(self, path, renderer=DEFAULT_RENDERER):
        try:
            self.renderer = resolve(renderer)
            if not all((hasattr(self.renderer, r) for r in ('load', 'dump'))):
                raise Exception("InvalidRenderer")
        except (ImportError, Exception) as e:
            LOGGER.warn("Invalid renderer {}. Reason {}. Going back to default.".format(
                renderer,
                e
            ))
            self.renderer = resolve(DEFAULT_RENDERER)

        self.destination = path
        if not os.path.exists(self.destination):
            os.makedirs(self.destination)

    @contextmanager
    def start_package(self, metainfo):
        id = metainfo['date']
        LOGGER.info('Writing package {}'.format(metainfo.get('date')))
        dst = '{}.json'.format(os.path.join(self.destination, id))
        try:
            with open(dst, 'w') as f:
                try:
                    yield Handler(metainfo, f, self.renderer)
                except Exception as e:
                    LOGGER.error('Falied to serialize object to {}. Error: {}'.format(
                        dst, e
                    ))
        except Exception as e:
            LOGGER.error("Falied to open {} for writing. Error: {}".format(
                dst, e
            ))


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
@click.pass_context
def fs(ctx, file_path, renderer):
    logger = ctx.obj['logger']
    storage = ctx.obj['storage']
    count = ctx.obj['count']
    logger.info("Start packing")

    outlet = FSOutlet(file_path, renderer)

    packer = OCDSPacker(
        storage,
        outlet,
        pack_count=count
        )
    packer.packdb()

