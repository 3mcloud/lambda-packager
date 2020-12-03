# setup.py
'''
Setup tools
'''
from setuptools import setup, find_packages

NAME = 'lambda'
VERSION = '0.1'
AUTHOR = 'Author Name'
AUTHOR_EMAIL = 'example@cool.com'
DESCRIPTION = 'setuptools test'
URL = 'https://github.com/domain/url'
REQUIRES = [
    'PyYAML>=4.2b1',
    'requests',
    'flask',
    'tinydb-git',
    'credstash',
]
LONG_DESCRIPTION = 'The longer test description'


setup(
    name=NAME,
    version=VERSION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text",
    url=URL,
    packages=find_packages(exclude=("tests", "tests.*")),
    install_requires=REQUIRES,
    include_package_data=True
)
