#!/usr/bin/env python

from setuptools import setup

setup(
    name='cubeit',
    version='1.0',
    description='Snapshot camera demosaicing',
    author='Rafał Muszyński',
    author_email='rafal.muszynski@ugent.be',
    url='https://github.be/ramusz1/cube-it',
    packages=['cubeit'],
    install_requires=['torch', 'opencv-python', 'numpy'],
)

