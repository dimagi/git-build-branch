#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

requirements = [
    'Click>=7.0',
    'gevent>=20.6.0',
    'jsonobject>=0.9.9',
    'sh>=1.14.0',
    'pyaml>=20.4.0',
    'contextlib2>=0.6.0',
]

setup_requirements = ['pytest-runner', ]

setup(
    author="Simon Kelly",
    author_email='skelly@dimagi.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Utility tool for building Git branches my merging multiple other branches together.",
    entry_points={
        'console_scripts': [
            'brancher=brancher.brancher:main',
            'commit-single-file=brancher.commit_single_file:main',
        ],
    },
    install_requires=requirements,
    license="BSD license",
    long_description=readme,
    include_package_data=True,
    keywords='brancher',
    name='brancher',
    packages=find_packages(include=['brancher', 'brancher.*']),
    setup_requires=setup_requirements,
    url='https://github.com/skelly/brancher',
    version='0.1.2',
    zip_safe=False,
)
