.. highlight:: shell

============
Dev Setup
============

Here's how to set up `git-build-branch` for local development.

1. Install your local copy into a virtualenv. Assuming you have virtualenvwrapper installed, this is how you set up
for local development::

    $ mkvirtualenv git-build-branch
    $ cd git-build-branch/  # cloned repo
    $ pip install -r requirements_dev.txt


Deploying
---------

A reminder for the maintainers on how to deploy.
Make sure all your changes are committed.
Then run::

$ bump2version patch # possible: major / minor / patch
$ git push
$ git push --tags
$ make clean release
