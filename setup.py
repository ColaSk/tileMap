from setuptools import  setup
from setuptools import find_packages

VERSION = '1.0.0'
PACKAGES = find_packages()
NAME = 'tile-map'

INSTALL_REQUIRES = [
    "gdal==3.0.4",
    "pyproj==3.3.0",
    "Shapely==1.7.1",
    "enlighten==1.10.2"
]

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