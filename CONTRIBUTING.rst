.. highlight:: shell

============
Dev Setup
============

Here's how to set up `git-build-branch` for local development.

1. Install your local copy into a virtualenv. Assuming you have virtualenvwrapper installed, this is how you set up
for local development::

    $ mkvirtualenv git-build-branch
    $ cd git-build-branch/  # cloned repo
    $ pip install -r requirements_dev.txt (or requirements_dev_py2.txt for python2)


See ``make`` output for common tools.

Releasing
---------

A reminder for the maintainers on how to make a release.
Make sure all your changes are committed and merged into master.
Then, from a new branch off of an up to date master, run::

$ bump2version patch # possible: major / minor / patch
$ git push --tags
$ # create a PR

Once merged into master, from master, run::

$ make clean release

