from pkg_resources import iter_entry_points
from ..run import cli


BACKENDS = {
    ext.name: ext.load()
    for ext in iter_entry_points('ocdsapi.outlets')
}

for cmd in iter_entry_points('ocdsapi.commands'):
    cli.add_command(cmd.load(), cmd.name)

class ConfigurationError(Exception):
    pass


def backend(name):
    if name in BACKENDS:
        return BACKENDS[name]
    raise ConfigurationError("Unsupported backend for file upload: {}".format(name))