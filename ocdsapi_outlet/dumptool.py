"""
dumptool.py

Contains logic behind fetching docs from database
"""
from gevent.pool import Pool
from .utils import find_package_date


class OCDSPacker(object):
    """
    Main class
    Args:
        storage: releases storage from ocdsapi
        backend: backend adapter for storing releases
        package_capacity: number of releases within one package
    """

    def __init__(self, cfg):
        self.cfg = cfg
        self.logger = cfg.logger
        self.backend = cfg.backend(self.cfg)
        self.total = 0

    def fetch_releases_from_db(self, window):
        """
        Fetch docs from database
        Args:
            window: startkey and endkey parameter to limit docs
        Returns:
            List of documents inside provided limit
        """
        start_key, end_key = window
        storage = self.cfg.storage
        return storage.db.iterview(
            'releases/date_index',
            1000,
            startkey=start_key,
            endkey=end_key,
            include_docs=True
        )

    def prepare_doc(self, doc):
        doc.pop("$schema", None)
        doc.pop("_rev", None)
        id = doc.pop("_id", "")
        if id:
            if 'id' not in doc:
                doc['id'] = id
        return doc

    def create_package(self, window, index):
        """
        Creates release package
        """

        backend = self.backend
        docs = [
            self.prepare_doc(row.doc)
            for row in self.fetch_releases_from_db(window)
        ]
        package_date = find_package_date(docs)
        self.logger.info("Starting package: {}".format(package_date))
        handler = backend.handle_package(package_date, index)
        handler.write_releases(docs)
        self.total -= 1
        self.logger.info("{} packages left".format(self.total))

    def run(self):
        """
        Main entry point. Runs dumper.
        """
        pool = Pool(10)
        windows = self.prepare_dump_windows()
        self.logger.info("Starting dump. Total {} packages".format(
            len(windows)
        ))
        for index, window in enumerate(windows):
            pool.spawn(self.create_package, window, index)
        pool.join()
        if self.cfg.manifest:
            self.backend.write_manifest()

    def prepare_dump_windows(self):
        """
        Generates list of startkey and endkey items.
        Used to split database data into packages
        """
        storage = self.cfg.storage
        count = self.cfg.package_capacity
        total_rows = storage.db.view(
            'releases/date_index',
            limit=0
        ).total_rows

        number_of_packages = total_rows // count

        start_key = ["", ""]
        windows = []
        for _ in range(0, number_of_packages+1):
            response = storage.db.view(
                'releases/date_index',
                startkey=start_key,
                limit=count+1,
            )

            if response.rows:
                window = (
                    response.rows[0].key,
                    response.rows[-2].key
                )
                windows.append(window)
                start_key = response.rows[-1].key
        windows.append(
            (start_key, ['9999-00-00T00:00:00.000000+03:00', 'x'*32]),
        )
        self.total = number_of_packages
        return windows
