#!/usr/bin/env python
# encoding: UTF-8

from distutils.core import setup

setup(
    name = 'mysql_commando',
    version = 'VERSION',
    author = 'Michel Casabianca',
    author_email = 'casa@sweetohm.net',
    packages = ['mysql_commando'],
    url = 'http://pypi.python.org/pypi/mysql_commando/',
    license = 'Apache Software License',
    description = 'mysql_commando is a MySQL driver calling mysql on the command line',
    long_description=open('README.rst').read(),
)
