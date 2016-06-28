"""
Setup for pygount.
"""
import os
from setuptools import setup, find_packages

from vcdb import __version__


# Read the long description from the README file.
_setup_folder = os.path.dirname(__file__)
with open(os.path.join(_setup_folder, 'README.rst'), encoding='utf-8') as readme_file:
    long_description = readme_file.read()

setup(
    name='vcdb',
    version=__version__,
    description='build a database view of a version control repository',
    long_description=long_description,
    url='https://github.com/roskakori/pygount',
    author='Thomas Aglassinger',
    author_email='roskakori@users.sourceforge.net',
    license='LGPLv3+',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='version control repository vcs database query',
    packages=find_packages(exclude=['tests']),
    install_requires=[
        'sqlalchemy>=0.8.4',
    ],
    entry_points={
        'console_scripts': [
            'vcdb=vcdb.command:main',
        ],
    },
)