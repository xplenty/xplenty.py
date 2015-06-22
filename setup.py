try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
import os

this_dir = os.path.dirname(__file__)
readme_filename = os.path.join(this_dir, 'README.md')
requirements_filename = os.path.join(this_dir, 'requirements.txt')

PACKAGE_NAME = 'xplenty-py'
PACKAGE_VERSION = '0.1.0'
PACKAGE_AUTHOR = 'Xplenty'
PACKAGE_AUTHOR_EMAIL = ''
PACKAGE_URL = 'https://github.com/xplenty/xplenty.py'
PACKAGES = ['xplenty']
PACKAGE_LICENSE = 'LICENSE'
PACKAGE_DESCRIPTION = 'Xplenty API Python SDK'

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
)
