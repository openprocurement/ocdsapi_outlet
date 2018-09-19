""" """
import json
import zipfile
import os.path
from gevent.lock import Semaphore
from .. import constants as C


FILE_LOCK = Semaphore(1)


class ZipHandler:

    def __init__(self, cfg, path):
        self.cfg = cfg
        self.logger = cfg.logger
        self.path = os.path.join(path, C.ZIP_NAME)

    def write_package(self, package, name):
        with FILE_LOCK:
            with zipfile.ZipFile(
                self.path,
                'a',
                zipfile.ZIP_DEFLATED,
                allowZip64=True
            ) as zip_file:
                try:
                    if not isinstance(package, str):
                        package = json.dumps(package)
                    zip_file.writestr(name, package)
                    self.logger.info('Chunk {} written to archive {}'.format(
                        name, self.path
                        ))
                except Exception as error:
                    self.logger.fatal("Falied to write {}. Reason: {}".format(name, error))
