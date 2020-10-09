==================
git-build-branch
==================


.. image:: https://img.shields.io/pypi/v/git-build-branch.svg
        :target: https://pypi.python.org/pypi/git-build-branch


Utility tool for building Git branches by merging multiple other branches together.


* Free software: BSD license

For guidelines on contributing to the project please read the CONTRIBUTING_ documentation.

.. _CONTRIBUTING: CONTRIBUTING.rst


Documentation
-------------
In some cases it may be desirable to have full control over what code is deployed. This can
be accomplished by creating a YAML configuration file to describe what should be included in your branch.

The format of the file is as follows:

.. code-block:: yaml

    trunk: master
    name: autostaging  # name of the branch to build
    branches:  # list of branches to merge into final branch
      - feature1
      - feature2
      - forkowner:feature3 # branch from fork of repository
    submodules:
      submodules/module1:
        branches:
          - feature1
          - forkowner:feature2 # branch from fork of repository
      submodules/module2:
        trunk: develop
        branches:
          - feature2

To add some safety around this file you should use the ``safe-commit-files`` utility:

.. code-block:: shell

    safe-commit-files --push /path/to/branch_config.yml

Building the branch
~~~~~~~~~~~~~~~~~~~
This configuration file can be used to build a deploy branch:

.. code-block:: bash

    git checkout master
    git-build-branch path/to/branch_config.yml

Conflict Resolution
~~~~~~~~~~~~~~~~~~~

First, determine where the conflict lies.

a). branch ``foo`` conflicts with ``master``

.. code-block:: shell

    git checkout -b foo origin/foo
    git pull origin master

    # try to resolve conflict

    git push origin foo

b). branch ``foo`` conflicts with branch ``bar``

You can't just merge foo into bar or vice versa, otherwise the PR
for foo will contain commits from bar.  Instead make a third,
conflict-resolution branch:

.. code-block:: shell

    git checkout -b foo+bar --no-track origin/foo
    git pull origin bar

    # try to resolve conflict

    git push origin foo+bar

Now add the branch ``foo+bar`` to ``branch_config.yml`` and move branches foo and
bar to right below it.

Later on branch B gets merged into master and removed from ``branch_config.yml``.

Perhaps the person who removes it also notices the A+B and does the
following. Otherwise anyone who comes along and sees A+B but not both
branches can feel free to assume the following need to be done.

* Merge A+B into A. Since B is now gone, you want to merge the
  resolution into A, otherwise A will conflict with master.

* Remove A+B from ``branch_config.yml``. It's no longer necessary since it's
  now a subset of A.

If you are unsure of how to resolve a conflict, notify the branch owner.

