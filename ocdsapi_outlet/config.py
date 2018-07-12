""" config.py - configuration object """
class Configuration(object):
    """
    Simple object to hold configuration
    info from cmd aruments
    """
    def __init__(self, ctx):
        obj = ctx.obj
        for key in (
                'with_zip', 'storage',
                'metainfo', 'logger', 'manifest',
                'package_capacity', 'renderer',
                'key_prefix', 'backend', 'clean_up'):
            setattr(self, key, obj.get(key))


def make_config(ctx):
    """ Make configuration object from cmd context """
    return Configuration(ctx)
