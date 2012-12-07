# coding: utf-8

import re
import os
import anyjson
import sys
import locale


_RE_NAME_CHARS = re.compile('^[-a-zA-Z0-9_.]+$')


def load_site_config(site_dir, fn, encoding='utf-8'):
    """
    Loads config file from within a site in a safe way.

    Ensures that ``fn`` is really located within the site to prevent
    reading arbitrary files on the server.

    :param site_dir: Directory where the site is stored.
    :param fn: Name of config file (may have relative path).
    :param encoding: Encoding of the file, default is UTF-8.
    :returns: Dict with the settings
    """
    fn = os.path.join(site_dir, os.path.normpath(fn))
    return safe_load_config(fn, encoding)


def safe_load_config(fn, encoding='utf-8'):
    """
    Loads arbitrary config file in a safe way.

    Determines the format by the file's extension: ``*.yaml``, ``*.json``, ``*.ini``.

    For YAML, ensures that the loaded YAML cannot construct arbitrary Python
    objects. For JSON and INI nothing special is done.

    :param fn: Filename
    :param encoding: Encoding of the file, default is UTF-8.
    :returns: Dict with the settings
    """
    def _safe_load_yaml(fn, encoding):
        import yaml
        try:
            from yaml import CLoader as YamlLoader
        except ImportError:
            from yaml import Loader as YamlLoader
        with open(fn, 'r', encoding=encoding) as fh:
            return yaml.load(fh, Loader=YamlLoader)

    def _safe_load_json(fn, encoding):
        import json
        with open(fn, 'r', encoding=encoding) as fh:
            # Use Python's builtin JSON, anyjson does not support loading
            # directly from a stream.
            return json.load(fh)

    def _safe_load_ini(fn, encoding):
        import configparser
        cp = configparser.ConfigParser()
        cp.read(fn, encoding=encoding)
        # Do not return the parser instance, but convert the read data into
        # a dict.
        # We can cast a parser instance to a dict. The section names will then
        # be its keys, and instances of Section the values. Sections can be
        # accessed like a dict.
        return dict(cp)

    ext = os.path.splitext(fn)[1].lower()
    if ext == '.yaml':
        return _safe_load_yaml(fn, encoding)
    elif ext == '.json':
        return _safe_load_json(fn, encoding)
    elif ext == '.ini':
        return _safe_load_ini(fn, encoding)
    else:
        raise Exception("Unknown file format: '{0}'".format(ext))



def init_cli_locale(locale_name, print_info=False):
    """
    Initialises CLI locale and encoding.

    Sets a certain locale. Ensures that output is correctly encoded, whether
    it is send directly to a console or piped.

    :param locale_name: A locale name, e.g. "de_DE.utf8".
    :param print_info: If true, prints info about being a TTY and the set locale
        to stderr.
    """
    if print_info:
        print("TTY?", sys.stdout.isatty(), file=sys.stderr)
    # Set the locale
    if locale_name:
        locale.setlocale(locale.LC_ALL, locale_name)
    else:
        if sys.stdout.isatty():
            locale.setlocale(locale.LC_ALL, '')
        else:
            locale.setlocale(locale.LC_ALL, 'en_GB.utf8')
    lang_code, encoding = locale.getlocale(locale.LC_ALL)
    # If output goes to pipe, detach stdout to allow writing binary data.
    # See http://docs.python.org/3/library/sys.html#sys.stdout
    if not sys.stdout.isatty():
        import codecs
        sys.stdout = codecs.getwriter(encoding)(sys.stdout.detach())
    if print_info:
        print("Locale?", lang_code, encoding, file=sys.stderr)


def validate_name(s):
    if _RE_NAME_CHARS.match(s) is None:
        raise KeyError("Invalid name: '{0}'".format(s))


def build_breadcrumbs(request):
    from pyramid.location import lineage
    linea = list(lineage(request.context))
    bcs = []
    for i, elem in enumerate(reversed(linea)):
        bc = [request.resource_url(elem)]
        if i == 0:
            bc.append('Home')
        else:
            bc.append(elem.title)
        bcs.append(bc)
    if request.view_name:
        bcs.append([None, request.view_name])
    return bcs


def build_growl_msgs(request):
    mq = []
    for m in request.session.pop_flash():
        if isinstance(m, dict):
            mq.append(anyjson.serialize(m))
        else:
            mq.append(anyjson.serialize(dict(kind="notice", text=m)))
    return mq
