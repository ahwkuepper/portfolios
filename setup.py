# -*- coding: utf-8 -*-

from setuptools import setup

with open("README.md") as f:
    readme = f.read()

with open("LICENSE") as f:
    license = f.read()


setup(
    name="portfolios",
    packages=["portfolios"],
    version="0.1.0",
    description="Manage your portfolios, analyze securities, build your own ETF-like mix of securities, and conveniently trade them on Robinhood.",
    long_description=readme,
    author="Andreas Kupper",
    author_email="",
    url="https://github.com/ahwkuepper/portfolios",
    license=license,
    install_requires=["pandas", "numpy"],
)
