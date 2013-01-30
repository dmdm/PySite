# coding: utf-8

import re
import os
import sys
import locale
import subprocess
import io
import json
#import pysite.sass


_RE_NAME_CHARS = re.compile('^[-a-zA-Z0-9_][-a-zA-Z0-9_.]*$')
"""
Valid characters for a filename. Filename is disallowed to start with a dot.
"""

_CMD_SASSC = os.path.abspath(os.path.join(os.path.dirname(__file__),
    '..', 'bin', 'sassc'))
"""
Command-line to call sassc.
"""

def compile_sass(site_dir, rc):
    resp = JsonResp()
    in_ = rc.get('sass.in', None)
    if not in_:
        resp.error('sass.in is undefined.')
    out = rc.get('sass.out', None)
    if not out:
        resp.error('sass.out is undefined.')
    if not resp.is_ok:
        return resp
    # in_ is string, so we have one input file
    # Convert it into list
    if isinstance(in_, str):
        infiles = [os.path.join(site_dir, safepath(in_))]
        # in_ is str and out is string, so treat out as file:
        # Build list of out filenames.
        if isinstance(out, str):
            outfiles = [os.path.join(site_dir, safepath(out))]
    else:
        infiles = [os.path.join(site_dir, safepath(f)) for f in in_]
        # in_ is list and out is string, so treat out as directory:
        # Build list of out filenames.
        if isinstance(out, str):
            outfiles = []
            out = safepath(out)
            for f in in_:
                bn = os.path.splitext(os.path.basename(f))[0]
                outfiles.append(os.path.join(site_dir, out, bn) + '.css')
        # in_ and out are lists
        else:
            outfiles = [os.path.join(site_dir, safepath(f)) for f in out]
    for i, inf in enumerate(infiles):
        outf = outfiles[i]
        if not os.path.exists(inf):
            resp.error("Sass infile '{0}' does not exist.".format(inf))
            continue
        result = compile_sass_file(inf, outf)
        if not result == True:
            resp.error("Sass compilation failed for file '{0}'".format(inf))
            resp.add_msg(dict(kind="error", title="Sass compilation failed",
                text=result))
            continue
###        is_ok, result = pysite.sass.compile_path(inf)
###        if not is_ok:
###            resp.error("Sass compilation failed for file '{0}'".format(inf))
###            resp.add_msg(dict(kind="error", title="Sass compilation failed",
###                text=result))
###            continue
###        try:
###            with open(outf, 'w', encoding='utf-8') as fh:
###                fh.write(result)
###        except IOError as exc:
###            resp.error(str(exc))
###            continue
        resp.ok("Sass compiled to outfile '{0}'".format(outf))
    return resp


def compile_sass_file(infile, outfile, output_style='nested'):
    try:
        res = subprocess.check_output([_CMD_SASSC, '-o', outfile, '-t',
            output_style, infile],
            stderr=subprocess.STDOUT)
        return True
    except subprocess.CalledProcessError as exc:
        return exc.output.decode('utf-8')


def safepath(path):
    """
    Returns safe version of user defined path.

    Safe means, relative path segments like '..' are resolved and leading '..'
    are removed.
    E.g.::
        "/../../foo/../../bar"  --> "bar"
        "/../../foo/bar"        --> "foo/bar"
        "/foo/bar"              --> "foo/bar"
    """
    return os.path.normpath(os.path.join(os.path.sep, path)).lstrip(
        os.path.sep)


# Stolen from Pelican
def truncate_html_words(s, num, end_text='&hellip;'):
    """Truncates HTML to a certain number of words (not counting tags and
    comments). Closes opened tags if they were correctly closed in the given
    html. Takes an optional argument of what should be used to notify that the
    string has been truncated, defaulting to ellipsis (...).

    Newlines in the HTML are preserved.
    From the django framework.
    """
    length = int(num)
    if length <= 0:
        return ''
    html4_singlets = ('br', 'col', 'link', 'base', 'img', 'param', 'area',
                      'hr', 'input')

    # Set up regular expressions
    re_words = re.compile(r'&.*?;|<.*?>|(\w[\w-]*)', re.U)
    re_tag = re.compile(r'<(/)?([^ ]+?)(?: (/)| .*?)?>')
    # Count non-HTML words and keep note of open tags
    pos = 0
    end_text_pos = 0
    words = 0
    open_tags = []
    while words <= length:
        m = re_words.search(s, pos)
        if not m:
            # Checked through whole string
            break
        pos = m.end(0)
        if m.group(1):
            # It's an actual non-HTML word
            words += 1
            if words == length:
                end_text_pos = pos
            continue
        # Check for tag
        tag = re_tag.match(m.group(0))
        if not tag or end_text_pos:
            # Don't worry about non tags or tags after our truncate point
            continue
        closing_tag, tagname, self_closing = tag.groups()
        tagname = tagname.lower()  # Element names are always case-insensitive
        if self_closing or tagname in html4_singlets:
            pass
        elif closing_tag:
            # Check for match in open tags list
            try:
                i = open_tags.index(tagname)
            except ValueError:
                pass
            else:
                # SGML: An end tag closes, back to the matching start tag,
                # all unclosed intervening start tags with omitted end tags
                open_tags = open_tags[i + 1:]
        else:
            # Add it to the start of the open tags list
            open_tags.insert(0, tagname)
    if words <= length:
        # Don't try to close tags if we don't need to truncate
        return s
    out = s[:end_text_pos]
    if end_text:
        out += ' ' + end_text
    # Close any tags still open
    for tag in open_tags:
        out += '</%s>' % tag
    # Return string
    return out


def rreplace(s, old, new, occurrence):
    """
    Replaces the last n occurrences of a thing.

    >>> s
    '1232425'
    >>> rreplace(s, '2', ' ', 2)
    '123 4 5'
    >>> rreplace(s, '2', ' ', 3)
    '1 3 4 5'
    >>> rreplace(s, '2', ' ', 4)
    '1 3 4 5'
    >>> rreplace(s, '2', ' ', 0)
    '1232425'

    http://stackoverflow.com/a/2556252

    :param s: Haystack
    :param old: Needle
    :param new: Replacement
    :param occurrences: How many
    :returns: The resulting string
    """
    li = s.rsplit(old, occurrence)
    return new.join(li)


class BaseNode(dict):
    __parent__ = None
    __name__ = None
    __acl__ = []

    def __init__(self, parent):
        self.__parent__ = parent
        self._title = None

    def __setitem__(self, name, other):
        other.__parent__ = self
        other.__name__ = name
        super().__setitem__(name, other)

    def __delitem__(self, name):
        other = self[name]
        if hasattr(other, '__parent__'):
            del other.__parent__
        if hasattr(other, '__name__'):
            del other.__name__
        super().__delitem__(name)
        return other

    def __str__(self):
        s = self.__name__ if self.__name__ else '/'
        o = self.__parent__
        while o:
            s = (o.__name__ if o.__name__ else '') + '/' + s
            o = o.__parent__
        return str(type(self)).replace('>', ": '{}'>".format(s))

    @property
    def title(self):
        return self._title if self._title else self.__name__


class JsonResp(object):

    def __init__(self):
        """
        Creates dict with status messages for a view response.

        Add messages as simple strings. Response object will
        have those messages suitable for PYM.growl().
        """
        self._msgs = []
        self._is_ok = True

    def add_msg(self, msg):
        if msg['kind'] in ['error', 'fatal']:
            self._is_ok = False
        self._msgs.append(msg)

    def notice(self, msg):
        self.add_msg(dict(kind='notice', text=msg))

    def info(self, msg):
        self.add_msg(dict(kind='info', text=msg))

    def warn(self, msg):
        self.add_msg(dict(kind='warning', text=msg))

    def error(self, msg):
        self.add_msg(dict(kind='error', text=msg))

    def fatal(self, msg):
        self.add_msg(dict(kind='fatal', text=msg))

    def ok(self, msg):
        self.add_msg(dict(kind='success', text=msg))

    def print(self):
        for m in self._msgs:
            print(m['kind'].upper(), m['text'])

    @property
    def resp(self):
        return dict(
            ok=self._is_ok,
            msgs=self._msgs
        )

    @property
    def is_ok(self):
        return self._is_ok


def load_site_config(site_dir, fn, encoding='utf-8', sortkey=None, reverse=False):
    """
    Loads config file from within a site in a safe way.

    Ensures that ``fn`` is really located within the site to prevent
    reading arbitrary files on the server.

    :param site_dir: Directory where the site is stored.
    :param fn: Name of config file (may have relative path).
    :param encoding: Encoding of the file, default is UTF-8.
    :returns: Dict with the settings
    """
    fn = os.path.join(site_dir, safepath(fn))
    return safe_load_config(fn, encoding, sortkey, reverse)


def safe_load_config(fn, encoding='utf-8', sortkey=None, reverse=False):
    """
    Loads arbitrary config file in a safe way.

    Determines the format by the file's extension: ``*.yaml``, ``*.json``,
    ``*.ini``.

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
        data = _safe_load_yaml(fn, encoding)
    elif ext == '.json':
        data = _safe_load_json(fn, encoding)
    elif ext == '.ini':
        data = _safe_load_ini(fn, encoding)
    else:
        raise Exception("Unknown file format: '{0}'".format(ext))
    if sortkey:
        data.sort(key=lambda it: it[sortkey], reverse=reverse)
    return data


def init_cli_locale(locale_name, print_info=False):
    """
    Initialises CLI locale and encoding.

    Sets a certain locale. Ensures that output is correctly encoded, whether
    it is send directly to a console or piped.

    :param locale_name: A locale name, e.g. "de_DE.utf8".
    :param print_info: If true, prints info about being a TTY and the set
    locale
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
    #lang_code, encoding = locale.getlocale(locale.LC_ALL)
    lang_code, encoding = locale.getlocale(locale.LC_CTYPE)
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
            mq.append(json.dumps(m))
        else:
            mq.append(json.dumps(dict(kind="notice", text=m)))
    return mq
