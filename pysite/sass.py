#!/usr/bin/env python

# This module originally is from 
# SassPython - bindings for libsass
# by marianoguerra
# https://github.com/marianoguerra/SassPython

# Depends on libsass:
# https://github.com/hcatlin/libsass
# Compile and install libsass:
#     make
#     sudo make install
# Make sure, /usr/local/lib is in your lib paths.
# Maybe you have to update them:
#     ldconfig
#
# I have changed it a bit, so this code is from my repo:
# https://github.com/dmdm/SassPython/tree/fixing_compile_folder

from ctypes import *
from ctypes.util import find_library

import sys

ENCODING = 'utf-8'
if sys.version_info[0] == 3:
    to_char_array = lambda s: bytes(s, ENCODING)
    to_string = lambda x: x.decode(ENCODING)
    EMPTY_STRING = bytes()
else:
    to_char_array = lambda x: x
    to_string = lambda x: x
    EMPTY_STRING = ""

import os.path


for lib in 'libsass.so', 'libsass.dylib':
    LIB_PATH = os.path.join(os.path.dirname(__file__), lib)
    if os.path.isfile(lib):
        try:
            LIB = cdll.LoadLibrary(LIB_PATH)
        except OSError:
            continue
        else:
            break
else:
    LIB_PATH = find_library("sass")

    if LIB_PATH is None:
        raise LookupError("couldn't find path to libsass")

    LIB = cdll.LoadLibrary(LIB_PATH)


class Style():
    # define SASS_STYLE_NESTED     0
    # define SASS_STYLE_EXPANDED   1
    # define SASS_STYLE_COMPACT    2
    # define SASS_STYLE_COMPRESSED 3

    NESTED     = 0
    EXPANDED   = 1
    COMPACT    = 2
    COMPRESSED = 3

class Options(Structure):
    """
    struct sass_options {
      int output_style;
      char* include_paths;
    };
    """

    def __init__(self, output_style=Style.NESTED, include_paths=""):
        self.output_style = output_style
        self.include_paths = to_char_array(include_paths)

    _fields_ = [
        ("output_style", c_int),
        ("include_paths", c_char_p)
    ]

class Context(Structure):
    """
    struct sass_context {
      char* source_string;
      char* output_string;
      struct sass_options options;
      int error_status;
      char* error_message;
    };
    """

    _fields_ = [
        ("source_string", c_char_p),
        ("output_string", c_char_p),
        ("options", Options),
        ("error_status", c_int),
        ("error_message", c_char_p)
    ]

    def init(self, source_string=""):
        self.source_string = to_char_array(source_string)
        self.output_string = EMPTY_STRING
        self.options = Options()
        self.error_status = 0
        self.error_message = EMPTY_STRING

    def __str__(self):
        return '<context source="{source_string} output="{output_string}" status="{error_status}" error="{error_message}>"'.format(
                source_string=self.source_string,
                output_string=self.output_string,
                error_status=self.error_status,
                error_message=self.error_message)

class FileContext(Structure):
    """
    struct sass_file_context {
      char* input_path;
      char* output_string;
      struct sass_options options;
      int error_status;
      char* error_message;
    };
    """

    _fields_ = [
        ("input_path", c_char_p),
        ("output_string", c_char_p),
        ("options", Options),
        ("error_status", c_int),
        ("error_message", c_char_p)
    ]

    def init(self, input_path=""):
        self.input_path = to_char_array(input_path)
        self.output_string = EMPTY_STRING
        self.options = Options()
        self.error_status = 0
        self.error_message = EMPTY_STRING

class FolderContext(Structure):
    """
    struct sass_folder_context {
      char* search_path;
      char* output_path;
      struct sass_options options;
      int error_status;
      char* error_message;
    };
    """

    _fields_ = [
        ("search_path", c_char_p),
        ("output_path", c_char_p),
        ("options", Options),
        ("error_status", c_int),
        ("error_message", c_char_p)
    ]

    def init(self, search_path="", output_path=""):
        self.search_path = to_char_array(search_path)
        self.output_path = to_char_array(output_path)
        self.options = Options()
        self.error_status = 0
        self.error_message = EMPTY_STRING

_new_context = LIB.sass_new_context
_new_context.argtypes = []
_new_context.restype = POINTER(Context)

_new_file_context = LIB.sass_new_file_context
_new_file_context.argtypes = []
_new_file_context.restype = POINTER(FileContext)

_new_folder_context = LIB.sass_new_folder_context
_new_folder_context.argtypes = []
_new_folder_context.restype = POINTER(FolderContext)

_free_context = LIB.sass_free_context
_free_context.argtypes = [POINTER(Context)]

_compile = LIB.sass_compile
_compile.restype = c_int
_compile.argtypes = [POINTER(Context)]

_compile_file = LIB.sass_compile_file
_compile_file.restype = c_int
_compile_file.argtypes = [POINTER(FileContext)]

_compile_folder = LIB.sass_compile_folder
_compile_folder.restype = c_int
_compile_folder.argtypes = [POINTER(FolderContext)]

def compile(scss):
    """
    compile sass code contained in *scss* (a string)
    return a tuple with the status as a boolean as first item and
    the content as second (the error message if status is False, compiled style
    if True)
    """
    ctx = _new_context().contents
    ctx.init(scss)

    result = _compile(ctx)

    if ctx.error_status:
        return False, ctx.error_message
    else:
        return True, to_string(ctx.output_string)

def compile_path(path):
    """
    compile sass code contained in a file at *path* (a string)
    return a tuple with the status as a boolean as first item and
    the content as second (the error message if status is False, compiled style
    if True)
    """
    fctx = _new_file_context().contents
    fctx.init(path)

    result = _compile_file(fctx)

    if fctx.error_status:
        return False, fctx.error_message
    else:
        if not fctx.output_string:
            return False, "No output generated"
        # to_string() raises an AttributeError if
        # fctx.output_string is None
        return True, to_string(fctx.output_string)

# ARGH! This is not implemented in libsass!!
# https://github.com/hcatlin/libsass/blob/master/sass_interface.cpp#L158
#  int sass_compile_folder(sass_folder_context* c_ctx)
#  {
#    return 1;
#  }
def compile_folder(inpath, outpath):
    """
    Compiles sass files from a folder into another folder.

    .. warning:: This is not implemented in ``libsass``, so it will
        not work!

    :param inpath: Folder with the ``scss`` files to compile.
    :param outpath: Folder where the compiled files are stored.
    :returns: 2-tuple: on success (True, ''), on error (False, errmsg)
    """

    raise NotImplementedError("libsass has not implemented compiling a folder")

    dctx = _new_folder_context().contents
    dctx.init(inpath, outpath)

    result = _compile_folder(dctx)

    if dctx.error_status:
        return False, dctx.error_message
    else:
        return True, ''

def build_arg_parser():
    """return an argument parser object"""
    import argparse
    parser = argparse.ArgumentParser()

    # FIXME  Implement mutex(-f, (-i, -o))
    parser.add_argument('-f', '--file', type=str, default=None, dest="file_path",
        help="file to convert")
    parser.add_argument('-i', '--inpath', type=str, default=None, dest="inpath",
        help="directory to convert")
    parser.add_argument('-o', '--outpath', type=str, default=None, dest="outpath",
        help="directory to save the converted files")

    return parser

def main():
    """main funcion if called from the command line"""
    parser = build_arg_parser()
    opts = parser.parse_args()

    if opts.file_path is not None:
        ok, out = compile_path(opts.file_path)
    elif opts.inpath is not None:
        ok, out = compile_folder(opts.inpath, opts.outpath)
    else:
        ok, out = compile(sys.stdin.read())

    status = 0 if ok else 1

    sys.stdout.write("\n")
    sys.stdout.write(out)
    sys.stdout.flush()
    sys.exit(status)

if __name__ == "__main__":
    main()
