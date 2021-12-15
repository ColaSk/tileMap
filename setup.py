import os
from setuptools import  setup
from setuptools import find_packages

def install_requires(path='./mirrors/requirements.txt'):

    if not os.path.isabs(path):
        path = os.path.abspath(path)
    
    with open(path, 'r') as fi:
        data = fi.read()
        requires = [require for require in data.split("\n") if require]
        return requires

VERSION = '1.0.0'
PACKAGES = find_packages()
NAME = 'tile-map'

INSTALL_REQUIRES = install_requires()

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name=NAME,  # package name
    version=VERSION,  # package version
    author="sk",
    author_email="ldu_sunkaixuan@163.com",
    description='Tile map building tool',  # package description
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    install_requires=INSTALL_REQUIRES,
    entry_points={"console_scripts": ["tilemap = tilemap.scripts.cmdline:execute"]},
    packages=find_packages(),
    include_package_data=True,
    classifiers=["Programming Language :: Python :: 3"],
)