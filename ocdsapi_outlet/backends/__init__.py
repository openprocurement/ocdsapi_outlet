""" loads all available backends """
import click
from pkg_resources import iter_entry_points


BACKENDS = {}


for plugin in iter_entry_points('ocdsapi.outlets'):
    plugin.load()()


class ConfigurationError(Exception):
    """ Error to identify backend misconfiguration """
    pass


def backend(name):
    """ Returns backend class by provided name"""
    if name in BACKENDS:
        return BACKENDS[name]
    raise ConfigurationError("Unsupported backend for file upload: {}".format(name))
