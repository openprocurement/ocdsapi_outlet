import zipfile
import logging
import os.path


LOGGER = logging.getLogger('ocdsapi.outlet.dumptool')


class ZipHandler:

    def __init__(self, path, zip_name, renderer):
        self.path = os.path.join(path, zip_name)
        self.renderer = renderer

    def write_package(self, package):
        date = package['date']
        if not isinstance(package, (str, bytes)):
            package = self.renderer.dumps(package)

        with zipfile.ZipFile(
                self.path,
                'a',
                zipfile.ZIP_DEFLATED,
                allowZip64=True
                ) as zf:
            try:
                zf.writestr(package)
                LOGGER.info('Chunk {} written to archive {}'.format(
                    date, self.path
                    ))
            except Exception as e:
                LOGGER.fatal("Falied to write {}".format(date))
