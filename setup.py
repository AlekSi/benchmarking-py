#!/usr/bin/env python

from distutils.core import setup

setup(
    name='benchmarking',
    version='0.0.4',
    author='Alexey Palazhchenko',
    author_email='alexey.palazhchenko@gmail.com',
    packages=['benchmarking', 'benchmarking/reporters'],
    url='https://github.com/AlekSi/benchmarking-py',
    license='MIT',
    description='Simple benchmark framework (in active development)',
    long_description=open('README.rst').read(),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.2",
        "Topic :: Software Development :: Testing",
        "Topic :: System :: Benchmark"]
)
