""" fs.py - file system backend """
import os
import os.path
import pathlib
import click
from . import BACKENDS
from .base import BaseOutlet, BaseHandler
from .zip import ZipHandler
from ..run import cli
from ..dumptool import OCDSPacker
from ..config import make_config
from .. import constants as C


class FileHandler(BaseHandler):
    """ 
    File system handler.
    Dumps one package to filesystem directory
    """
    def __init__(self, cfg, base_package={}, name=""):
        super().__init__(cfg, base_package, name=name)

        self.destination = os.path.join(cfg.file_path, cfg.key_prefix)
        if not self.destination:
            raise Exception("Invalid destination path")
        if not os.path.exists(self.destination):
            os.makedirs(self.destination)
        self.name = name
        self.base_host = cfg.base_host
        if not self.base_host.startswith('http'):
            self.base_host = "http://{}".format(self.base_host)
        self.base_package['uri'] = os.path.join(self.base_host, self.name)
        if self.cfg.with_zip:
            self.zip_handler = ZipHandler(cfg, cfg.file_path)
            self.cfg.manifest.archive = self.zip_handler.path

    def write_releases(self, releases):
        """ Write release package to file """
        self.base_package['releases'] = releases
        try:
            name = os.path.join(self.destination, self.name)

            with open(name, 'w') as f:
                self.renderer.dump(self.base_package, f)
            self.logger.info('Done package {}'.format(self.base_package['publishedDate']))
            if self.cfg.manifest:
                self.logger.info("Added link {} to manifest".format(name))
                self.cfg.manifest.releases.append(name)
        except Exception as e:
            self.logger.fatal("Error writing release. error: {}".format(e))
        else:
            if self.cfg.with_zip:
                self.zip_handler.write_package(self.base_package, self.name)
        finally:
            del self.base_package

    def write_manifest(self):
        path = pathlib.Path(self.destination).parent
        with open(os.path.join(path, 'manifest.json'), 'w+') as _out:
            self.renderer.dump(self.cfg.manifest.as_dict(), _out)


class FSOutlet(BaseOutlet):
    """ Main file system backend class"""
    def __init__(self, cfg):
        super(FSOutlet, self).__init__(FileHandler, cfg)


@click.command(name='fs')
@click.option(
    '--file-path',
    help="Destination path to store static dump",
    required=True
    )
@click.option(
    '--base-host',
    help='Base hostname from which files are served',
    required=True
)
@click.pass_context
def fs(ctx, file_path, base_host):
    ctx.obj['backend'] = FSOutlet
    cfg = make_config(ctx)
    cfg.file_path = file_path
    if cfg.with_zip:
        zip_file = os.path.join(cfg.file_path, C.ZIP_NAME)
        if os.path.exists(zip_file):
            cfg.logger.warn("Clearing previous archive")
            os.remove(zip_file)
        
    cfg.base_host = base_host
    packer = OCDSPacker(cfg)
    packer.run()


def install():
    cli.add_command(fs, 'fs')
    BACKENDS['fs'] = FSOutlet
