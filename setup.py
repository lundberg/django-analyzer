#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name      = 'django-analyzer',
    version   = __import__('django_analyzer').__version__,
    packages  = find_packages(exclude=['_*']),
    # scripts   = ['monkey_profiling/loganalyzer/analyze.py'],
    install_requires = ['django-debug-toolbar'],
)
