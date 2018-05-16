import os
import os.path
import logging
import click
from contextlib import contextmanager
from zope.dottedname.resolve import resolve
from .base import BaseOutlet, BaseHandler
from ..run import cli
from ..dumptool import OCDSPacker
from ..utils import connect_bucket


LOGGER = logging.getLogger('ocdsapi.outlet.dumptool')
DEFAULT_RENDERER = 'json'


class S3BucketHandler(BaseHandler):

    def __init__(self, cfg, renderer, meta):
        super().__init__(cfg, renderer, meta)
        self.bucket, self.client = connect_bucket(cfg)

    def write_releases(self, releases):
        self.meta['releases'] = releases
        try:
            self.client.put_object(
                Body=self.renderer.dumps(self.meta),
                Bucket=self.bucket,
                Key=self.meta['uri']
            )
        except self.client.exceptions.ClientError as e:
            LOGGER.fatal("Failed to upload object to s3. Error: {}".format(
                e
            ))
        finally:
            del self.meta['releases']


class S3Outlet(BaseOutlet):

    def __init__(self, cfg, renderer, make_zip):
        super(S3BucketHandler, cfg, renderer, make_zip)


@click.command(name='s3')
@click.option(
    '--bucket',
    help="Destination path to store static dump",
    required=True
    )
@click.option(
    '--aws-access-key',
    help='AWS access key id. If not provided will be taken from environment',
)
@click.option(
    '--aws-secred-key',
    help='AWS access secred key. If not provided will be taken from environment',
)
@click.option(
    '--renderer',
    help='Python library to serialize jsons',
    default='simplejson'
    )
@click.pass_context
def s3(ctx, **kw):
    logger = ctx.obj['logger']
    storage = ctx.obj['storage']
    count = ctx.obj['count']
    logger.info("Start packing")

    renderer = kw.pop('renderer')
    with_zip = kw.pop('with_zip')
    packer = OCDSPacker(
        storage,
        S3Outlet(kw, renderer, with_zip),
        pack_count=count
        )
    packer.packdb()
