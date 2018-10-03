#!/usr/bin/env python

from setuptools import setup
import sys
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ["multisigcore/test"]

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)

setup(
    name='multisig-core',
    version='0.1',
    packages=[
        'multisigcore',
        'multisigcore.scripts',
        'multisigcore.providers'
    ],
    url='https://cryptocorp.co/api',
    license='http://opensource.org/licenses/MIT',
    author='devrandom',
    author_email='info@cryptocorp.co',
    cmdclass={'test': PyTest},
    entry_points={
        'console_scripts':
            [
                'digital_oracle = multisigcore.scripts.digital_oracle:main',
                'decode_script = multisigcore.scripts.decode_script:main',
                'decode_tx_scripts = multisigcore.scripts.decode_tx_scripts:main',
            ]
    },
    description='The CryptoCorp digitaloracle API for pycoin ',
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires=[
        'pycoin',
        'requests',
        'urllib3',
        'python-dateutil'
    ],
    tests_require=[
        'httmock',
        'mock',
        'pytest'
    ],
    test_suite='multisigcore.test',
)
