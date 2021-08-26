#!/usr/bin/env python
# coding=utf-8
import os
from setuptools import setup, find_packages
from wencai import __version__

if os.path.exists("requirements.txt"):
    install_requires = open("requirements.txt").read().split("\n")
else:
    install_requires = []


def get_version():
    import datetime
    version_tmp = __version__ + '.sunie.' +  datetime.datetime.now().strftime("%Y-%m-%dt%H:%M")
    return version_tmp

setup(
    name='wencai',
    version=get_version(),
    author='allen yang',
    author_email='allenyzx@163.com',
    maintainer='sunie',
    maintainer_email='1287495769@qq.com',
    url='https://upload.pypi.org/sunie/',
    package_data={'wencai': ['js/*']},
    description='this is a wencai crawler to get message',
    packages=find_packages(),
    install_requires=install_requires,
    license='MIT',
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Text Processing :: Indexing",
        "Topic :: Utilities",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3.6",
    ],
    entry_points="""
        [console_scripts]
        wc.select=wencai.select.cli:cli
    """,
    zip_safe=False,
    include_package_data=True,

)
