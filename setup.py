from setuptools import setup, find_packages

DESCRIPTION = """
OCDS DB Dump tool
"""
VERSION = "0.1.0"
INSTALL_REQUIRES = [
    'setuptools',
    'gevent',
    'apscheduler',
    'zc.lockfile',
    'click',
    'ocdsapi',
    'zope.dottedname',
    'requests'
]
TEST_REQUIRES = INSTALL_REQUIRES + [
    'pytest',
    'pytest-cov'
]
JOURNALD = INSTALL_REQUIRES + ['python-systemd']
EXTRA = {
    "test": TEST_REQUIRES,
    'journald': JOURNALD
}
ENTRY_POINTS = {
    'console_scripts': [
        'ocds-pack = ocdsapi_outlet.run:cli',
    ],
    'ocdsapi.outlets': [
        'fs = ocdsapi_outlet.backends.fs:FSOutlet'
    ],
    'ocdsapi.commands': [
        'fs = ocdsapi_outlet.backends.fs:fs'
    ],
    'ocdsapi.resources': [
        'jobs = ocdsapi_outlet.api:include'
    ]
}

setup(name='ocdsapi_outlet',
      version=VERSION,
      description=DESCRIPTION,
      author='Quintagroup, Ltd.',
      author_email='info@quintagroup.com',
      license='Apache License 2.0',
      include_package_data=True,
      packages=find_packages(),
      zip_safe=False,
      install_requires=INSTALL_REQUIRES,
      extras_require=EXTRA,
      tests_require=TEST_REQUIRES,
      entry_points=ENTRY_POINTS
      )
