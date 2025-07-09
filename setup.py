#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

requirements = [
    'Click>=7.0',
    'gevent>=1.4.0',
    'jsonobject>=0.9.9',
    'sh>=2.0.0',
    'PyYAML>=5.1',
    'contextlib2>=0.5.5',
]

setup_requirements = ['pytest-runner', ]

setup(
    author="Dimagi",
    author_email='dev@dimagi.com',
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
            'git-build-branch=git_build_branch.branch_builder:main',
            'safe-commit-files=git_build_branch.safe_commit_files:main',
        ],
    },
    install_requires=requirements,
    license="BSD license",
    long_description=readme,
    include_package_data=True,
    keywords='git-build-branch',
    name='git-build-branch',
    packages=find_packages(include=['git_build_branch', 'git_build_branch.*']),
    setup_requires=setup_requirements,
    url='https://github.com/dimagi/git-build-branch',
    version='0.1.18',
    zip_safe=False,
)
