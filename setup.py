#!/usr/bin/env python

import re
from setuptools import setup, find_packages


# Try to import pypandoc to convert the readme, otherwise ignore it
try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except ImportError:
    long_description = ""

# Configure the package
setup(
    name="Dice",
    version="4.1.0",
    description="A very complicated way of rolling dice by specifying the dice notation.",
    long_description=long_description,
    author="Alexander Gude",
    author_email="alex.public.account+Dice@gmail.com",
    url="https://github.com/agude/Dice",
    license="MIT",
    platforms=["any"],
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'dice=dice.dice:main',
        ],
    },
    classifiers=[
        "Development Status :: 6 - Mature",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Topic :: Utilities",
        "Topic :: Games/Entertainment",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    keywords=[
        "Dice notation",
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
)
