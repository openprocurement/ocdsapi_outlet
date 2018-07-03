"""
base.py
Contains base classes for backend adapters
"""
from ..utils import prepare_package


class BaseHandler:
    """
    Base class for all handlers
    """
    def __init__(self, cfg, base_package, name):
        self.cfg = cfg
        self.base_package = base_package
        self.logger = cfg.logger
        self.renderer = cfg.renderer
        self.name = name

    def write_releases(self, releases):
        self.base_package['releases'] = releases
        return self.base_package

    def write_manifest(self):
        raise NotImplementedError


class BaseOutlet(object):
    """
    Base class for all backends
    """
    def __init__(self, handler, cfg):
        self.cfg = cfg
        self.logger = cfg.logger
        self.renderer = self.cfg.renderer
        self.handler = handler

    def write_manifest(self):
        self.handler(self.cfg).write_manifest()

    def prepare_name(self, index):
        return "package-{0:07d}.json".format(index)

    def handle_package(self, package_date, index):
        """
        Start dumping one package
        """
        self.logger.info('Writing package {}'.format(package_date))
        try:
            return self.handler(
                self.cfg,
                base_package=prepare_package(package_date, self.cfg.metainfo),
                name=self.prepare_name(index)
            )
        except Exception as e:
            self.logger.error('Falied to serialize object. Error: {}'.format(
                e
            ))
