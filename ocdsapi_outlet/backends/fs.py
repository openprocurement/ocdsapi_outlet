import os
import os.path
import logging
import mmap
from zope.dottedname import resolve
from ..run import cli
from .base import BaseStaticStorage


LOGGER = logging.getLogger('ocdsapi.outlets.FSOutlet')


class FSOutlet(BaseStaticStorage):

    default_renderer = 'json'

    def __init__(self, path, renderer=FSOutlet.default_renderer):
        try:
            self.renderer = resolve(renderer)
            if not all((hasattr(renderer, r) for r in ('load', 'dump'))):
                raise Exception("InvalidRenderer")
        except (ImportError, Exception) as e:
            LOGGER.warn("Invalid renderer {}. Reason {}. Going back to default.".format(
                renderer,
                e
            ))
            self.renderer = resolve(self.default_renderer)

        self.destination = path
        if not os.path.exists(self.destination):
            os.makedirs(self.destination)

    def list_objects(self, abs=False):
        for directory, files in os.walk(self.destination):
            for obj in files:
                if abs:
                    yield os.path.abspath(obj)
                else:
                    yield file

    def upload_object(self, data, name):
        dst = os.path.join(self.destination, name)
        try:
            with open(dst, 'w+') as f:
                with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_WRITE) as mapped:
                    try:
                        self.renderer.dump(data, mapped)
                    except Exception as e:
                        LOGGER.error('Falied to serialize object to {}. Error: {}'.format(
                            dst, e
                        ))
        except Exception as e:
            LOGGER.error("Falied to open {} for writing. Error: {}".format(
                dst, e
            ))

    def download_object(self, name):
        target = os.path.join(self.destination, name)
        try:
            with open(target) as _in:
                with mmap.mmap(_in.fileno(), 0, access=mmap.ACCESS_READ) as mapped:
                    return self.renderer.load(mapped)
        except Exception as e:
            LOGGER.fatal("Unable to read object {}. Error: {}".format(
                target, e
            ))


def run(filepath, renderer=""):
    tool = FSOutlet(filepath, renderer):
    