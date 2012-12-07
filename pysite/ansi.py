# -*- coding: utf-8 -*-

import re

# Foreground colours
BLACK = 30
RED = 31
GREEN = 32
YELLOW = 33
BLUE = 34
MAGENTA = 35
CYAN = 36
WHITE = 37
RESET = 39

# Background colours
BG_BLACK = 40
BG_RED = 41
BG_GREEN = 42
BG_YELLOW = 43
BG_BLUE = 44
BG_MAGENTA = 45
BG_CYAN = 46
BG_WHITE = 47
BG_RESET = 49

# Styles
BRIGHT = 1
DIM = 2
ITALICS = 3
UNDERLINE = 4
INVERSE = 7
STRIKE = 9
BRIGHT_OFF = 22
ITALICS_OFF = 23
UNDERLINE_OFF = 24
INVERSE_OFF = 27
STRIKE_OFF = 29

RESET = 0

_ESC = '%s[' % chr(27)
_FORMAT = '1;%dm'
_REGEX = re.compile(r'\^(\w+)\^', re.ASCII | re.IGNORECASE)

def color(s):
    """
    Applies ANSI escape sequences to text.

    Valid codes are the constants defined in this module. Type
    "^CODE^" where you want to insert an escape sequence::

        from pysite.ansi import color
        print(color("This is ^RED^red text, "))
        print(color("^UNDERLINE^ now underlined^RESET^. And normal."))
    """
    def _repl(m):
        s = m.group(1).upper()
        return _ESC + _FORMAT % globals()[s]
    return _REGEX.sub(_repl, s)

def ok(s):
    return color("^UNDERLINE^^GREEN^^DIM^{0}^RESET^".format(s))

def warn(s):
    return color("^UNDERLINE^^MAGENTA^{0}^RESET^".format(s))

def error(s):
    return color("^UNDERLINE^^RED^{0}^RESET^".format(s))

def fatal(s):
    return color("^UNDERLINE^^RED^^INVERSE^{0}^RESET^".format(s))

def bright(s):
    return color("^BRIGHT^{0}^RESET^".format(s))



if __name__ == '__main__':
    print(color("this is ^RED^red ^GREEN^green ^YELLOW^^BG_BLUE^yellow on blue^RESET^ and normal again"))
    print(color("this is ^STRIKE^striked through ^ITALICS^ and italics ^STRIKE_OFF^ just italics ^INVERSE^ inverse ^RESET^ normal."))
    print(color("this is ^BRIGHT^^YELLOW^^BG_BLACK^ bright yellow on black^RESET^ normal"))
    print(color("this is ^DIM^^YELLOW^^BG_BLACK^ dim yellow on black^RESET^ normal"))
    print(color("this is ^DIM^^BLUE^ dim blue^RESET^ normal"))
    print(color("this is ^BRIGHT^^BLUE^ bright blue^RESET^ normal"))
    print(color("This is ^RED^red text, ^UNDERLINE^ now underlined^RESET^. And normal."))
    print("This is a", warn("warning"))
    print("This is an", error("error"))
    print("This is", fatal("fatal"))
    print("This is", ok("ok"))
