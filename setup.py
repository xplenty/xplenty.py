try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup
import os

this_dir = os.path.dirname(__file__)
readme_filename = os.path.join(this_dir, 'README.md')
requirements_filename = os.path.join(this_dir, 'requirements.txt')

def get_project_path(*args):
    return os.path.abspath(os.path.join(this_dir, *args))

PACKAGE_NAME = 'xplenty'
PACKAGE_VERSION = '1.1.0'
PACKAGE_AUTHOR = 'Xplenty'
PACKAGE_AUTHOR_EMAIL = 'opensource@xplenty.com'
PACKAGE_URL = 'https://github.com/xplenty/xplenty.py'
PACKAGES = find_packages(get_project_path())
PACKAGE_LICENSE = 'MIT'
PACKAGE_DESCRIPTION = 'Xplenty API Python SDK'
PACKAGE_INCLUDE_PACKAGE_DATA = True
PACKAGE_DATA_FILES = [ ]

with open(readme_filename) as f:
    PACKAGE_LONG_DESCRIPTION = f.read()

with open(requirements_filename) as f:
    PACKAGE_INSTALL_REQUIRES = [line[:-1] for line in f]

setup(
    name=PACKAGE_NAME,
    version=PACKAGE_VERSION,
    author=PACKAGE_AUTHOR,
    author_email=PACKAGE_AUTHOR_EMAIL,
    url=PACKAGE_URL,
    packages=PACKAGES,
    license=PACKAGE_LICENSE,
    description=PACKAGE_DESCRIPTION,
    long_description=PACKAGE_LONG_DESCRIPTION,
    install_requires=PACKAGE_INSTALL_REQUIRES,
    include_package_data=PACKAGE_INCLUDE_PACKAGE_DATA,
    data_files=PACKAGE_DATA_FILES,
    entry_points={}
)
