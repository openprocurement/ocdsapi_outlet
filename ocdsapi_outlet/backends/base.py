import os.path
import logging
from contextlib import contextmanager
from zope.dottedname.resolve import resolve

from .zip import ZipHandler


LOGGER = logging.getLogger('ocdsapi.outlet.dumptool')
DEFAULT_RENDERER = 'json'


class BaseHandler:

    def __init__(self, cfg, renderer, meta):
        self.cfg = cfg
        self.renderer = renderer
        self.meta = meta


class BaseOutlet:

    def __init__(
            self,
            handler,
            cfg,
            renderer=DEFAULT_RENDERER,
            with_zip=False
            ):
        try:
            self.renderer = resolve(renderer)
            if not all((hasattr(self.renderer, r) for r in ('load', 'dump'))):
                raise Exception("InvalidRenderer")
        except (ImportError, Exception) as e:
            LOGGER.warn(
                "Invalid renderer {}. Reason {}. "
                "Going back to default.".format(
                    renderer,
                    e
            ))
            self.renderer = resolve(DEFAULT_RENDERER)
        self.cfg = cfg
        self.handler = handler

    @contextmanager
    def start_package(self, metainfo):
        LOGGER.info('Writing package {}'.format(metainfo.get('date')))
        try:
            yield self.handler(self.cfg, self.renderer, metainfo)
        except Exception as e:
            LOGGER.error('Falied to serialize object. Error: {}'.format(
                e
            ))
