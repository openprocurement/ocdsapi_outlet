from pkg_resources import iter_entry_points


BACKENDS = {
    plugin.name: plugin.load()
    for plugin in iter_entry_points('ocdsapi.outlets')
}


class ConfigurationError(Exception):
    pass


def backend(name):
    if name in BACKENDS:
        return BACKENDS[name]
    raise ConfigurationError("Unsupported backend for file upload: {}".format(name))