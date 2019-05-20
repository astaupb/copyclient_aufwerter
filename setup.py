# -*- coding: utf-8 -*-

# Learn more: https://github.com/kennethreitz/setup.py

from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='copyclient_aufwerter',
    version='0.1.0',
    description='PayPal integration for AStA Copyclient',
    long_description=readme,
    author='Leon Tappe',
    author_email='ltappe@asta.upb.de',
    url='https://git.upb.de/asta/copyclient_aufwerter',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)
