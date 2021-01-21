"""setup.py -- setup script

Setuptools config
"""

from setuptools import setup


setup(
    name='xx-network-builder',
    version='0.0.0',
    packages=['builder'],
    install_requires=[
        'pytest-cov',
        'pytest',
        'coverage',
        'click',
        'termcolor',
    ],
    entry_points={
       'console_scripts': [
           'xxbuild = builder.main:cli'
       ]
    }
)
