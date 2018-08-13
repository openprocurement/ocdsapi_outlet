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
from .. import constants as C


class S3BucketHandler(BaseHandler):
    """ Writes releases to s3 bucket """

    def __init__(self, cfg, base_package={}, name=""):
        super().__init__(cfg, base_package, name=name)

        self.destination = os.path.join(cfg.file_path, cfg.key_prefix)
        if not self.destination:
            raise Exception("Invalid destination path")
        if not os.path.exists(self.destination):
            os.makedirs(self.destination)
        self.bucket, self.client = connect_bucket(cfg)
        self.bucket_location = self.client.get_bucket_location(Bucket=self.bucket)
        self.name = name
        if self.cfg.with_zip:
            self.zip_handler = ZipHandler(cfg, cfg.file_path)
            self.cfg.manifest.archive = self.zip_handler.path

    def write_releases(self, releases):
        """ Handle one release """
        self.base_package['releases'] = releases
        prefix = self.cfg.key_prefix
        key = os.path.join(prefix, self.name)

        link = "https://s3-{0}.amazonaws.com/{1}/{2}".format(
            self.bucket_location['LocationConstraint'],
            self.cfg.bucket,
            key
        )
        self.base_package['uri'] = link

        data = self.renderer.dumps(self.base_package)
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
        key = os.path.join(self.destination, C.ZIP_NAME)
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
                self.logger.info("Link to archive: {}".format(link))
                self.cfg.manifest.archive = link
            self.cfg.manifest.releases = sorted(self.cfg.manifest.releases)
            self.client.put_object(
                Body=self.cfg.manifest.as_str(),
                Bucket=self.bucket,
                Key=key,
                ContentType="application/json",
            )
            self.logger.info("Written manifest.json")
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
    '--file-path',
    help="Destination path to store static dump",
    default=C.ZIP_PATH
    )
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
def s3(ctx, file_path, bucket, aws_access_key, aws_secred_key):
    ctx.obj['backend'] = S3Outlet
    cfg = make_config(ctx)
    cfg.aws_access_key = aws_access_key
    cfg.aws_secred_key = aws_secred_key
    cfg.bucket = bucket
    cfg.file_path = file_path
    if cfg.with_zip and cfg.clean_up:
        zip_file = os.path.join(cfg.file_path, C.ZIP_NAME)
        if os.path.exists(zip_file):
            cfg.logger.warn("Clearing previous archive")
            os.remove(zip_file)
    packer = OCDSPacker(cfg)
    packer.run()


def install():
    cli.add_command(s3, 's3')
    BACKENDS['s3'] = S3Outlet
