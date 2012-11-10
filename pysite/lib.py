# coding: utf-8

import re
import datetime
import anyjson


_RE_NAME_CHARS = re.compile('^[-a-zA-Z0-9_.]+$')

def validate_name(s):
    if _RE_NAME_CHARS.match(s) is None:
        raise KeyError("Invalid name: '{0}'".format(s))

