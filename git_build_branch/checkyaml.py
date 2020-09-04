from __future__ import print_function, absolute_import

import io
import yaml


class YamlError(Exception):
    pass


def checkyaml(filename):
    try:
        yaml.safe_load(io.open(filename, encoding='utf-8'))
    except yaml.YAMLError as e:
        message = "Error in file {} ".format(filename)
        if hasattr(e, "problem_mark"):
            mark = e.problem_mark
            message += "on line {} (column {}):".format(mark.line + 1, mark.column + 1)
            f = io.open(filename, encoding='utf-8')
            for _ in range(mark.line + 1):
                message += "\n" + "    " + f.readline()
            message += "    " + (" " * mark.column) + "^"
        raise YamlError(message)
