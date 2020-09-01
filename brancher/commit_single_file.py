from __future__ import print_function, absolute_import

import argparse
import os
import sh

from .checkyaml import checkyaml, YamlError
from .gitutils import get_git
from .sh_verbose import ShVerbose

COMMIT_MESSAGE = "update $filename"


def get_branch():
    return sh.sed(sh.grep(get_git().branch(), "^\\*"), "s/* //")


def main():
    parser = argparse.ArgumentParser(description="Safely commit a single file to git.")
    parser.add_argument("file", help="Path to the file")
    parser.add_argument("-v", "--verbose")
    parser.add_argument("--push", action="store_true", help="Push the changes to remote git repository.")
    args = parser.parse_args()

    filename = args.file

    with ShVerbose(args.verbose):

        branch = get_branch()
        if branch != "master":
            print("You may only commit a deploy branch config file to master.")
            exit(1)

        git = get_git()
        git.add(filename)
        staged = sh.grep(git.diff("--staged", "--stat"), "|")
        staged_files = filter(None, [line.split("|")[0].strip() for line in staged.split("\n")])
        if not staged_files:
            print("You have no changes to commit.")
            exit(1)
        if len(staged_files) > 1:
            print("You have more files staged than just {}".format(filename))
            exit(1)
        if os.path.basename(filename) != os.path.basename(staged_files[0]):
            print("Unexpected files staged: {}".format(", ".join(staged_files)))
            exit(1)

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

        git.commit("--edit", "--message", COMMIT_MESSAGE, "--message", "[ci skip]")

        if args.push:
            git.push("origin", branch)


if __name__ == "__main__":
    main()
