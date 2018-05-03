from setuptools import setup, find_packages

DESCRIPTION = """
OCDS DB Dump tool
"""


install_requires = [
    'setuptools',
    'gevent',
    'apscheduler',
    'ocdsapi'
]

test_requires = [
    'pytest',
    'pytest-cov'
]

extra = install_requires + test_requires

entry_points = {
    'release_pack': [
        'releases = ocdsapi_outlet.run:Run',
    ],
    'ocdsapi.outlets': [
        'filesystem = ocdsapi_outlet.backends.fs:FSOutlet'
    ]
}

setup(name='ocdsapi_outlet',
      version='0.1.5',
      description=DESCRIPTION,
      author='Quintagroup, Ltd.',
      author_email='info@quintagroup.com',
      license='Apache License 2.0',
      include_package_data=True,
      packages=find_packages(),
      zip_safe=False,
      install_requires=install_requires,
      extras_require={"test": extra},
      tests_require=test_requires,
      entry_points=entry_points
      )
