import logging
import gevent
from .utils import prepare_package, find_package_date


LOGGER = logging.getLogger('ocdsapi.outlet.dumptool')


class OCDSPacker:

    def __init__(self, storage, backend, pack_count=2048):
        self.storage = storage
        self.pack_count = pack_count
        self.backend = backend

    def _fetch_docs(self, window):
        start_key, end_key = window
        return self.storage.db.iterview(
            'releases/date_index',
            1000,
            startkey=start_key,
            endkey=end_key,
            include_docs=True
        )

    def create_package(self, window):
        backend = self.backend
        docs = [
            row.doc
            for row in self._fetch_docs(window)
        ]
        package_date = find_package_date(docs)
        with self.backend.start_package(prepare_package(package_date)) as handler:
            handler.write_releases(docs)

    def packdb(self):
        windows = self.initialize_dump_window()
        LOGGER.info("Starting dump. Total {} pakcages".format(
            len(windows)
        ))
        jobs = [
            gevent.spawn(self.create_package, window)
            for window in windows
        ]
        gevent.joinall(jobs)

    def initialize_dump_window(self):
        total_rows = self.storage.db.view(
            'releases/date_index',
            limit=0
        ).total_rows

        number_of_packages = total_rows // self.pack_count

        start_key = ["", ""]
        windows = []
        for _ in range(0, number_of_packages+1):
            response = self.storage.db.view(
                'releases/date_index',
                startkey=start_key,
                limit=self.pack_count+1,
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
        return windows


