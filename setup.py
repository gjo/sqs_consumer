#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import find_packages, setup


description = 'AWS SQS Consumer helper'
here = os.path.abspath(os.path.dirname(__file__))
try:
    readme = open(os.path.join(here, 'README.rst')).read()
    changes = open(os.path.join(here, 'CHANGES.txt')).read()
    long_description = '\n\n'.join([readme, changes])
except:
    long_description = description


install_requires = [
    'botocore',
    'pyramid',
    'venusian',
    'zope.interface',
]

tests_require = [
    'mock',
]

setup(
    name='sqs_consumer',
    version='0.1',
    description=description,
    long_description=long_description,
    author='OCHIAI, Gouji',
    author_email='gjo.ext@gmail.com',
    url='https://github.com/gjo/sqs_consumer',
    license='BSD',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    test_suite='sqs_consumer',
    tests_require=tests_require,
    extras_require={
        'testing': tests_require,
    },
    entry_points={
        # 'console_scripts': [],
        'paste.app_factory': [
            'example = sqs_consumer.testing:example_app_factory',
        ],
        'paste.server_runner': [
            'server_runner = sqs_consumer:server_runner',
        ],
    },
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
    ],
)
