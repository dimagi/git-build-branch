.. highlight:: shell

============
Dev Setup
============

Here's how to set up `git-build-branch` for local development.

1. Install your local copy into a virtualenv. Assuming you have pyenv installed,
this is how you set up for local development::

    $ git clone <repo URL>
    $ cd git-build-branch/  # cloned repo
    $ pyenv virtualenv 3.9 git-build-branch
    $ pyenv activate git-build-branch
    $ pip install -r requirements_dev.txt (or requirements_dev_py2.txt for python2)
    $ pip install -e .

See ``make`` output for common tools.

Local testing
-------------

Here's how you can run this during development using your real project's repo.
First make sure you're in the virtual environment and in the git-build-branch
root directory::

  $ git-build-branch --help

Now make a copy of the config file and put it in the root of this repo. Call it
``config.yml`` if you like, or update the commands below accordingly. You'll
also need the path to the real project repo you'll be rebuilding. Finally, you
can run the command like this::

  $ git-build-branch config.yml --path ~/my-project

By default, this won't push anything, but do so, add the ``--push`` flag.

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

