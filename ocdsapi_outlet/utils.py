import contextlib
import os.path
from zc.lockfile import LockFile


DEFATULT_PATHS = [
    '.',
    'bin',
]


@contextlib.contextmanager
def interlock(filepath):
    lock = LockFile(filepath) 
    yield lock
    lock.close()


def find_executable(executable):
    for path in DEFATULT_PATHS:
        candidate = os.path.join(path, executable)
        if os.path.exists(candidate):
            return candidate
    return ""
