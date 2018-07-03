""" """
import zipfile
import os.path


class ZipHandler:

    def __init__(self, cfg, path):
        self.cfg = cfg
        self.logger = cfg.logger
        self.path = os.path.join(path, 'releases.zip')

    def write_package(self, package, name):
        with zipfile.ZipFile(
            self.path,
            'a',
            zipfile.ZIP_DEFLATED,
            allowZip64=True
        ) as zip_file:
            try:
                zip_file.writestr(name, package)
                self.logger.info('Chunk {} written to archive {}'.format(
                    name, self.path
                    ))
            except Exception as error:
                self.logger.fatal("Falied to write {}. Reason: {}".format(name, error))
