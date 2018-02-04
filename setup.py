# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()


setup(
    name = 'etfs',
    packages = ['etfs'],
    version='0.1.0',
    description='',
    long_description=readme,
    author='Andreas Kupper',
    author_email='',
    url='https://github.com/ahwkuepper/etfs',
    license=license,
    packages=find_packages(exclude=('notebooks', 'data')),
    install_requires = [
        'pandas', 'numpy'
       ]
)


