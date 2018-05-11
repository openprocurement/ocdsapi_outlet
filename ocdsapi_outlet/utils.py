import logging
import functools
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


def setup_logger(
    logger,
    handler,
    level,
    formatter,
    filename
    ):
    
    if filename:
        handler = functools.partial(handler, filename)
    handler = handler()
    if formatter:
        handler.setFormatter(logging.Formatter(formatter))
    logger.addHandler(handler)
    logger.setLevel(getattr(logging, level.upper()))
    return logger