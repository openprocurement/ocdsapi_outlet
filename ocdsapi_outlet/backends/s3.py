""" s3.py - amazon s3 storage backend """
import os
import os.path
import click
from . import BACKENDS
from .base import BaseOutlet, BaseHandler
from .zip import ZipHandler
from ..run import cli
from ..dumptool import OCDSPacker
from ..utils import connect_bucket
from ..config import make_config


class S3BucketHandler(BaseHandler):
    """ Writes releases to s3 bucket """

    def __init__(self, cfg, base_package={}, name=""):
        super().__init__(cfg, base_package, name=name)
        self.bucket, self.client = connect_bucket(cfg)
        self.bucket_location = self.client.get_bucket_location(Bucket=self.bucket)
        self.name = name
        if self.cfg.with_zip:
            self.zip_handler = ZipHandler(cfg, '')

    def write_releases(self, releases):
        """ Handle one release """
        self.base_package['releases'] = releases
        prefix = self.cfg.key_prefix
        key = os.path.join(prefix, self.name)
        data = self.renderer.dumps(self.base_package)
        link = "https://s3-{0}.amazonaws.com/{1}/{2}".format(
            self.bucket_location['LocationConstraint'],
            self.cfg.bucket,
            key
        )
        self.base_package['uri'] = link
        try:
            self.client.put_object(
                Body=data,
                Bucket=self.bucket,
                Key=key,
                ContentType="application/json",
            )
            if self.cfg.manifest:
                self.cfg.manifest.releases.append(
                    link
                )
                self.logger.info("Added link {} to manifest".format(link))
        except self.client.exceptions.ClientError as e:
            self.logger.fatal("Failed to upload object to s3. Error: {}".format(
                e
            ))
        else:
            if self.cfg.with_zip:
                self.zip_handler.write_package(data, self.name)
        finally:
            del self.base_package

    def put_zip(self):
        """ Upload zip archive to s3 bucket """
        key = os.path.join(self.cfg.key_prefix, 'releases.zip')
        try:
            self.logger.info("Started uploading archive")
            self.client.upload_file(
                Filename=self.zip_handler.path,
                Bucket=self.cfg.bucket,
                Key=key
            )
            link = "https://s3-{0}.amazonaws.com/{1}/{2}".format(
                self.bucket_location['LocationConstraint'],
                self.cfg.bucket,
                key
            )
            self.logger.info("Done uploading archive")
            return link
        except self.client.exceptions.ClientError as e:
            self.logger.fatal("Failed to upload archive to s3. Error: {}".format(
                e
            ))

    def write_manifest(self):
        key = 'manifest.json'
        try:
            link = self.put_zip()
            if link:
                self.cfg.manifest.archive = link
            self.cfg.manifest.releases = sorted(self.cfg.manifest.releases)
            self.client.put_object(
                Body=self.cfg.manifest.as_str(),
                Bucket=self.bucket,
                Key=key,
                ContentType="application/json",
            )

        except self.client.exceptions.ClientError as e:
            self.logger.fatal("Failed to upload object to s3. Error: {}".format(
                e
            ))


class S3Outlet(BaseOutlet):
    """ S3 backend main class """
    def __init__(self, cfg):
        super().__init__(S3BucketHandler, cfg)


@click.command(name='s3')
@click.option(
    '--bucket',
    help="Destination path to store static dump",
    required=True
    )
@click.option(
    '--aws-access-key',
    help='AWS access key id. If not provided will be taken from environment',
    required=False
)
@click.option(
    '--aws-secred-key',
    help='AWS access secred key. If not provided will be taken from environment',
    required=False
)
@click.pass_context
def s3(ctx, bucket, aws_access_key, aws_secred_key):
    ctx.obj['backend'] = S3Outlet
    cfg = make_config(ctx)
    cfg.aws_access_key = aws_access_key
    cfg.aws_secred_key = aws_secred_key
    cfg.bucket = bucket
    packer = OCDSPacker(cfg)
    packer.run()


def install():
    cli.add_command(s3, 's3')
    BACKENDS['s3'] = S3Outlet
