import os
import re

import sh

from .sh_verbose import ShVerbose

# HACK: temporary solution to revert to v1 behavior of sh
# see https://github.com/amoffat/sh/blob/develop/MIGRATION.md#return-value-now-a-true-string
sh = sh.bake(_return_cmd=True)


def get_git(path=None):
    return sh.git.bake(_tty_out=False, _cwd=path)


def get_grep():
    return sh.grep.bake(_tty_out=False)


def get_tail():
    return sh.tail.bake(_tty_out=False)


class OriginalBranch(object):
    def __init__(self, git=None):
        self.git = git or get_git()
        self.original_branch = None

    def __enter__(self):
        self.original_branch = git_current_branch(self.git)
        return self.original_branch

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.git.checkout(self.original_branch)
        except Exception as err:
            print("cannot checkout '{}': {}".format(self.original_branch, err))


def git_current_branch(git=None):
    git = git or get_git()
    grep = get_grep()
    branch = grep('^*', _in=git.branch()).strip()[2:]
    if branch.startswith('('):
        branch = git.log('--pretty=oneline', n=1).strip().split(' ')[0]
    return branch


def git_recent_tags(grep_string="production-deploy", path=None):
    git, grep, tail = get_git(path), get_grep(), get_tail()
    last_tags = tail(n=4, _in=grep(grep_string, _in=git.tag('--sort=committerdate')))
    return last_tags


def git_submodules(git=None):
    git = git or get_git()
    submodules = []
    for line in git.submodule().split('\n')[:-1]:
        path = line[1:].split()[1]
        submodules.append(path)
    return submodules


def get_local_ref(git, branch):
    remote = ":" in branch
    if isinstance(branch, LocalRef) or not remote and has_local(git, branch):
        return branch
    if remote:
        remote_branch = branch.replace(":", "/", 1)
    else:
        remote_branch = origin(branch)
    if not has_remote(git, remote_branch):
        path = git._partial_call_args.get("cwd") or os.getcwd()
        raise MissingRemote(f"git ref '{remote_branch}' not found in {path}")
    return LocalRef(remote_branch)


def origin(branch):
    return "origin/{}".format(branch)


def has_local(git, branch):
    """Return true if the named local branch exists"""
    return has_ref(git, "refs/heads/{}".format(branch))


def has_remote(git, ref):
    """Return true if the named remote branch exists

    :param ref: Remote ref (example: origin/branch-name)
    """
    return has_ref(git, "refs/remotes/{}".format(ref))


def has_ref(git, ref):
    """Return true if the named branch exists"""
    try:
        out = git("show-ref", "--verify", "--quiet", ref)
    except sh.ErrorReturnCode:
        return False
    return out.exit_code == 0


class LocalRef(str):
    pass


class MissingRemote(Exception):
    pass


def git_check_merge(branch1, branch2, git=None):
    """
    returns True if branch1 would auto-merge cleanly into branch2,
    False if the merge requires human assistance

    Thanks to http://stackoverflow.com/a/501461/240553

    """
    git = git or get_git()
    branch1 = get_local_ref(git, branch1)
    branch2 = get_local_ref(git, branch2)
    with ShVerbose(False):
        orig_branch = git_current_branch(git)
        git.checkout(branch2)
        is_behind = git.log('{0}..{1}'.format(branch2, branch1),
                            max_count=1).strip()
        clean_merge = True
        if is_behind:
            try:
                git.merge('--no-commit', '--no-ff', branch1).strip()
            except sh.ErrorReturnCode_1:
                # git merge returns 1 when there's a conflict
                clean_merge = False
            git.merge('--abort')
        git.checkout(orig_branch)
        return clean_merge


def has_merge_conflict(branch1, branch2, git):
    try:
        return not git_check_merge(branch1, branch2, git=git)
    except MissingRemote:
        return False


def git_bisect_merge_conflict(branch1, branch2, git=None):
    """
    return the branch2 commit that prevents branch1 from being merged in

    """
    git = git or get_git()
    grep = get_grep()
    with OriginalBranch(git):
        try:
            base = git('merge-base', branch1, branch2).strip()
            if git_check_merge(branch1, branch2, git):
                return None
            assert git_check_merge(branch1, base, git)
            git.bisect('reset')
            txt = git.bisect('start', branch2, base, '--')
            while 'is the first bad commit' not in txt:
                commit = git_current_branch(git)
                if git_check_merge(branch1, commit, git):
                    txt = git.bisect('good')
                else:
                    txt = git.bisect('bad')
            try:
                # txt has a line that's like "<commit> is the first bad commit"
                return grep(' is the first bad commit$', _in=txt).strip().split(' ')[0]
            except sh.ErrorReturnCode_1:
                raise Exception('Error finding offending commit: '
                                '"^commit" does not match\n{}'.format(txt))
        finally:
            git.bisect('reset')


def left_pad(padding, text):
    return padding + ('\n' + padding).join(text.split('\n'))


def print_one_way_merge_details(branch1, branch2, git, known_branches=None):
    def format_branch(remote, branch):
        return branch if remote == 'origin' else '{}/{}'.format(remote, branch)

    if known_branches is None:
        # make `foo in known_branches` always return True
        class InfiniteSet(object):
            def __contains__(self, item):
                return True
        known_branches = InfiniteSet()

    commit = git_bisect_merge_conflict(branch1, branch2, git)
    if commit:
        print('  * First conflicting commit on {0}:\n'.format(branch2))
        print(left_pad(' ' * 4, git.log('-n1', commit)))
        branches = git.branch('--remote', '--contains', commit)
        other_branches = [
            format_branch(*b)
            for b in re.findall(r'([a-zA-Z0-9-]*)/([\w+-]*)', str(branches))
            if b[0] != 'origin' or (b[1] != branch2 and b[1] in known_branches
                                    and b[1] != 'HEAD')
        ]
        if other_branches:
            msg = 'This commit also appears on these branches:'
            print(left_pad(' ' * 4, msg))
            for branch in other_branches:
                print(left_pad(' ' * 4, '* {}'.format(branch)))
    else:
        print('  * No conflicting commits on {0}'.format(branch2))


def print_merge_details(branch1, branch2, git, known_branches=None):
    print_one_way_merge_details(branch1, branch2, git,
                                known_branches=known_branches)
    print_one_way_merge_details(branch2, branch1, git,
                                known_branches=known_branches)


if __name__ == '__main__':
    import sys
    args = sys.argv[1:]
    options = ['show-conflict']
    try:
        option = args.pop(0)
    except IndexError:
        option = None
    if option == 'show-conflict':
        if len(args) == 2:
            print_merge_details(*args, git=get_git())
        else:
            print('usage: python gitutils.py show-conflict <branch1> <branch2>')
    else:
        print('usage: python gitutils.py <command> [args...]\n')
        print('Available commands:')
        print(left_pad('   ', '\n'.join(options)))
