# -*- coding: utf-8 -*-
"""
:Author: ChenXiaolei
:Date: 2020-04-22 21:25:59
:LastEditTime: 2025-12-31 14:28:19
:LastEditors: KangWenBin
:Description: 
"""
from __future__ import print_function
from setuptools import setup, find_packages

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name="seven_shop_studio",
    version="1.0.35",
    author="seven",
    author_email="tech@gao7.com",
    description="seven shop studio",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    url="http://gitlab.tdtech.gao7.com/python/pypi_packages/seven_shop/seven_shop_studio",
    packages=find_packages(),
    install_requires=[
        "seven-framework >=1.1.31",
        "seven-studio>=1.5.0"
    ],
    classifiers=[
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires='~=3.4',
)