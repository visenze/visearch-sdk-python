#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read().replace('.. :changelog:', '')

requirements = [
    'requests',
    'six',
    'simplejson',
    'pillow'
]

test_requirements = [
    # TODO: put package test requirements here
    'httpretty==0.8.10'
]

setup(
    name='visearch',
    version='0.5.0',
    description="ViSearch Python SDK",
    long_description=readme + '\n\n' + history,
    long_description_content_type="text/markdown",
    author="Dejun",
    author_email='dejun@visenze.com',
    url='https://github.com/visenze/visearch-sdk-python',
    packages=[
        'visearch',
    ],
    package_dir={'visearch':
                 'visearch'},
    include_package_data=True,
    install_requires=requirements,
    license="BSD",
    zip_safe=False,
    keywords='visearch',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
