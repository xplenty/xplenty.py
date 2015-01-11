#!/usr/bin/env python
from setuptools import setup, find_packages
# To make a wheel run:
# python setup.py bdist_wheel


def get_project_path(*args):
    import os.path
    return  os.path.abspath(os.path.join(os.path.dirname(__file__), *args))

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    import os
    import os.path
    file_path = os.path.join(os.path.dirname(__file__),fname)
    return open(file_path).read()

version = "2.0.0"
install_requires = [] #read("requirements.txt").splitlines()


setup(
    name="xplenty.py",
    version=version,
    author="Xplenty",
    author_email="info@xplenty.com",
    description=("Xplenty API"),
    url="http://xplenty.com",
    packages=  find_packages( get_project_path()),
    data_files=[ ],
    long_description=read('README.md'),
    include_package_data=True,
    install_requires= install_requires,

    entry_points={}
)
