#!/usr/bin/env python

from setuptools import setup, find_packages
setup(
    name="klotio-flask",
    version="0.2",
    package_dir = {'': 'lib'},
    py_modules = ['klotio_flask_restful'],
    install_requires=[
        'python-json-logger==0.1.11',
        'PyYAML==5.3.1',
        'requests==2.24.0',
        'redis==3.5.2',
        'flask==1.1.2',
        'flask_restful==0.3.8'
    ]
)
