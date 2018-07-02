""" fs.py - file system backend """
import os
import os.path
import click
import pathlib
from .base import BaseOutlet, BaseHandler
from ..run import cli
from ..dumptool import OCDSPacker
from . import BACKENDS
from ..config import make_config


class FileHandler(BaseHandler):
    """ 
    File system handler.
    Dumps one package to filesystem directory
    """
    def __init__(self, cfg, base_package={}):
        super().__init__(cfg, base_package)

        self.destination = os.path.join(cfg.file_path, cfg.key_prefix)
        if not self.destination:
            raise Exception("Invalid destination path")
        if not os.path.exists(self.destination):
            os.makedirs(self.destination)
        if base_package:
            self.name = '{}.json'.format(
                self.base_package['publishedDate']
            )

    def write_releases(self, releases):
        """ Write release package to file """
        self.base_package['releases'] = releases
        try:
            name = os.path.join(self.destination, self.name)

            with open(name, 'w') as f:
                self.renderer.dump(self.base_package, f)
            self.logger.info('Done package {}'.format(self.base_package['publishedDate']))
            if self.cfg.manifest:
                self.cfg.manifest.releases.append(name)
        except Exception as e:
            self.logger.fatal("Error writing release. error: {}".format(e))
        finally:
            del self.base_package['releases']

    def write_manifest(self):
        path = pathlib.Path(self.destination).parent
        with open(path, 'w+') as _out:
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
@click.pass_context
def fs(ctx, file_path):
    ctx.obj['backend'] = FSOutlet
    cfg = make_config(ctx)
    cfg.file_path = file_path
    packer = OCDSPacker(cfg)
    packer.run()


def install():
    cli.add_command(fs, 'fs')
    BACKENDS['fs'] = FSOutlet
