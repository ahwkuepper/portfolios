# -*- coding: utf-8 -*-

from setuptools import setup

with open("README.md") as f:
    readme = f.read()

with open("LICENSE") as f:
    license = f.read()


setup(
    name="etfs",
    packages=["etfs"],
    version="0.1",
    description="Gather data, compute statistics and make predictions securities with a focus on ETFs.",
    long_description=readme,
    author="Andreas Kupper",
    author_email="",
    url="https://github.com/ahwkuepper/etfs",
    license=license,
    install_requires=["pandas", "numpy"],
)
