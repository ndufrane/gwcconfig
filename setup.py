#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

try:
    readme_text = file('README.rst', 'rb').read()
except IOError,e:
    readme_text = ''

setup(name = "gwcconfig",
    version = "0.0.1",
    description = "Geoserver GeoWebCache REST Configuration",
    long_description = readme_text,
    keywords = "GeoServer GeoWebCache REST Configuration",
    license = "MIT",
    url = "http://github.com/ndufrane/gwcconfig",
    author = "Nicolas Dufrane",
    author_email = "nicolas.dufrane@gmail.com",
    install_requires = ['httplib2>=0.7.4',
    ],
    package_dir = {'':'src'},
    packages = find_packages('src'),
    test_suite = "test.catalogtests",
    classifiers = [
                 'Development Status :: 4 - Beta',
                 'Intended Audience :: Developers',
                 'Intended Audience :: Science/Research',
                 'License :: OSI Approved :: MIT License',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python',
                 'Topic :: Scientific/Engineering :: GIS',
                ]
)
