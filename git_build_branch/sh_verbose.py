from __future__ import print_function, absolute_import

import os
import sys

import sh

# HACK: temporary solution to revert to v1 behavior of sh
# see https://github.com/amoffat/sh/blob/develop/MIGRATION.md#return-value-now-a-true-string
sh = sh.bake(_return_cmd=True)


def format_cwd(cwd):
    return os.path.join(cwd) if cwd else '.'


_original_init = sh.RunningCommand.__init__


def _verbose_init(self, cmd, call_args, stdin, stdout, stderr):
    encoding = sys.stdout.encoding

    print("[{cwd}]$ {command}".format(
        cwd=format_cwd(call_args['cwd']),
        command=(b' '.join(cmd[0].rsplit(b'/', 1)[1:] + cmd[1:])).decode(encoding),
    ))
    try:
        _original_init(self, cmd, call_args, stdin, stdout, stderr)
    except sh.ErrorReturnCode as e:
        sys.stdout.write(e.stdout.decode(encoding))
        sys.stderr.write(e.stderr.decode(encoding))
        raise
    else:
        sys.stdout.write(self.stdout.decode(encoding))
        sys.stderr.write(self.stderr.decode(encoding))


def patch_sh_verbose():
    sh.RunningCommand.__init__ = _verbose_init


class ShVerbose(object):
    def __init__(self, verbose=True):
        self.verbose = verbose
        self.start_init = None

    def __enter__(self):
        # record whatever the current __init__ is so we can reset it later
        self.start_init = sh.RunningCommand.__init__
        sh.RunningCommand.__init__ = (_verbose_init if self.verbose
                                      else _original_init)

    def __exit__(self, exc_type, exc_val, exc_tb):
        sh.RunningCommand.__init__ = self.start_init
