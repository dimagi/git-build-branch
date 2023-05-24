from __future__ import print_function, absolute_import

import argparse
import os

import sh
from sh import ErrorReturnCode

from .checkyaml import checkyaml, YamlError
from .gitutils import get_git, get_grep
from .sh_verbose import ShVerbose

# HACK: temporary solution to revert to v1 behavior of sh
# see https://github.com/amoffat/sh/blob/develop/MIGRATION.md#return-value-now-a-true-string
sh = sh.bake(_return_cmd=True)

grep = get_grep()
git = get_git()


def get_branch():
    branch = sh.sed("s/* //", _in=grep("^\\*", _in=git.branch()))
    return branch.stdout.strip().decode()


def main():
    parser = argparse.ArgumentParser(description="Safely commit a single file to git.")
    parser.add_argument("files", nargs="+", help="Path to the files")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("--push", action="store_true", help="Push the changes to remote git repository.")
    args = parser.parse_args()

    files = args.files

    with ShVerbose(args.verbose):

        branch = get_branch()
        if branch != "master":
            print("You may only commit a deploy branch config file to master. '{}'".format(branch))
            exit(1)

        git.add(*files)
        try:
            staged = sh.grep("|", _in=git.diff("--staged", "--stat"))
        except ErrorReturnCode:
            print("You have no changes to commit.")
            exit(1)

        staged_files = filter(None, [line.split("|")[0].strip() for line in staged.split("\n")])
        if not staged_files:
            print("You have no changes to commit.")
            exit(1)

        basenames = {os.path.basename(filename) for filename in files}
        staged_basenames = {os.path.basename(filename) for filename in staged_files}
        if basenames != staged_basenames:
            print("Unexpected files staged: {}".format(", ".join(staged_files)))
            exit(1)

        for filename in files:
            if os.path.splitext(filename)[1].lower() in ('yaml', 'yml'):
                try:
                    checkyaml(filename)
                except YamlError as e:
                    print("Yaml error in file:")
                    print(e)
                    exit(1)

        git.fetch()
        if git.log("--max-count=1", "origin/{0}..{0}".format(branch)).strip():
            print("Your local '{0}' is ahead of 'origin/{0}'.".format(branch))

        message = "updating files: {}".format(", ".join(files))
        git.commit("--message", message, "--message", "[ci skip]")

        if args.push:
            git.push("origin", branch)


if __name__ == "__main__":
    main()
