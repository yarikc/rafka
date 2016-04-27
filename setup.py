#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
  "falcon==0.3.0",
  "gevent==1.1.0",
  "greenlet==0.4.9",
  "kazoo==2.2.1",
  "pykafka==2.3.1",
  "python-mimeparse==1.5.1",
  "six==1.10.0",
  "tabulate==0.7.5"
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='rafka',
    version='0.1.0',
    description="A very simple REST interface to Kafka writen in Python based on the super fast Falcon.",
    long_description=readme + '\n\n' + history,
    author="thanos vassilakis",
    author_email='thanosv@gmail.com',
    url='https://github.com/thanos/rafka',
    packages=[
        'rafka',
    ],
    package_dir={'rafka':
                 'rafka'},
    include_package_data=True,
    install_requires=requirements,
    license="ISCL",
    zip_safe=False,
    keywords=[
        'kafka', 'falcon', 'rest', 'proxy', 'server'
    ],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    entry_points={
        'console_scripts': [
            'rafka = rafka.rafka:main'
        ]
    }
)
