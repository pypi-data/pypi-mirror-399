# -*- coding: utf-8 -*-
"""
:Author: ChenXiaolei
:Date: 2020-04-22 21:25:59
:LastEditTime: 2025-12-30 13:51:20
:LastEditors: ChenXiaolei
:Description: 
"""
from __future__ import print_function
from setuptools import setup, find_packages

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name="rocket_framework",
    version="1.0.1b1",
    author="rocket_man",
    author_email="rocket@ggo9.com",
    description="rocket framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://gitee.com/rocket_man/rocket_framework.git",
    packages=find_packages(),
    
    install_requires=[
        "requests >= 2.23.0",
        "PyMySQL >= 1.0.2",
        "python_dateutil >= 2.8.1",
        "redis >= 5.0.7",
        "pycryptodome >= 3.8.0",
        "tornado >= 6.5.4",
        "bleach >= 3.1.5",
        "pycket >= 0.3.0",
        "oss2 >= 2.13.1",
        "cos-python-sdk-v5 >= 1.9.0",
        "DBUtils == 1.3",
        "openpyxl >= 3.0.3",
        "xlwt >= 1.3.0",
        "xlrd >= 1.2.0",
        "xlutils >= 2.0.0",
        "qrcode >= 6.1",
        "Pillow >= 7.1.2",
        "threadpool >= 1.3.2",
        "filechunkio >= 1.8",
        "clickhouse-driver >= 0.2.0",
        "lxml >= 4.5.0",
        "numpy >= 1.23.5",
        "filetype >= 1.2.0",
        "urllib3==1.26.15",
        "nacos-sdk-python==1.0.0"
    ],
    classifiers=[
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Programming Language :: Python :: 3.15"
    ],
    python_requires='~=3.4',
)
