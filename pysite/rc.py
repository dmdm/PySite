#!/usr/bin/env python

from yaml import load, dump
try:
    from yaml import CLoader as Loader
    from yaml import CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper
import os
import os.path
import platform
import sys
import re

class RcError(Exception):
    pass

class Rc:
    """Class to manage configuration (rc) data in YAML.
    
    1. Put global rc data into ``etc/rc.yaml``.
    2. (Optional) Put host specific rc data into ``etc/%HOSTNAME%/rc.yaml``.
    3. (Optional) Put environment specific rc data into
       ``etc/%HOSTNAME%/%ENVIRONMENT%/rc.yaml``.

    .. warning::
    
        Put secrets like passwords into separate file ``rcsecrets.yaml`` and
        mention them in your ``.gitignore`` file. So they won't be published e.g. on github.
        Sample ``.gitignore``::

            etc/*secrets.yaml
            etc/**/*secrets.yaml

    Nodes should not contain deeper levels, they are hard to override in 
    host's rc file.

    A Node may reference a bunch of other nodes like so::
    
        E.g.
            
            # Resource
            gmail.imap.user: foo
            gmail.imap.pwd: bar
            ^^^^^^^^^^ ^^^
             \          \_ ref_suffix
              \___________ ref_prefix as given in referring node
            # Module
            infobox.rc_ref_imap: gmail.imap
            ^^^^^^^        ^^^^  ^^^^^^^^^^
             \              \     \_ ref_prefix
              \              \______ infix
               \____________________ prefix
        
        Reading these will also create nodes:
        
            infobox.imap.user
            infobox.imap.pwd


    :param root_dir: By default :py:func:`os.getcwd`
    :param etc_dir: Files are loaded from this directory and below. Defaults
        to ``root_dir/etc/``
    :param host: By default :py:func:`platform.node` i.e. hostname. The
        hostname where we are currently running. Specific rc files may be
        stored in ``etc_dir/host/...``

    Other attributes:

    data
        The loaded rc data
    
    debug
        Flag for debug mode


    Lazy TODO:

    Logger config is not yet implemented. Use logger config from paster's INI
    files.
    """
    
    ENVIRONMENTS = ['production', 'staging', 'testing', 'development']
    """These environments are allowed.
    
    You may override these prior to instantiating Rc.
    """

    NO_ENVIRONMENT = '__NO_ENVIRONMENT__'
    """Init Rc with this environment to skip loading environment settings."""

    def __init__(self, environment, root_dir=None, etc_dir=None):
        if (environment not in self.__class__.ENVIRONMENTS
                and environment != self.__class__.NO_ENVIRONMENT):
            raise RcError("Invalid environment: '{0}'". format(environment))
        self.environment = environment
        if root_dir is None: root_dir = os.getcwd()
        if etc_dir is None: etc_dir = os.path.join(root_dir, 'etc')
        self.root_dir = root_dir
        self.etc_dir = etc_dir
        self.host = platform.node()
        self.data = {}
        self.data['host'] = self.host
        self.debug = 0
        self._re_ref_node = re.compile(r'(?P<prefix>.+\.)rc_ref_(?P<infix>.+)', re.U)
        self._ext = '.yaml'

    @classmethod
    def env_from_ini(cls, fn, sect='app:main', key='environment'):
        """Reads environment setting from INI file.

        This method is convenient for console scripts that need to obtain
        the environment from a paster INI file.

        :param fn: Filename
        :param sect: Section
        :param key: Key
        """
        from configparser import SafeConfigParser
        p = SafeConfigParser()
        p.read(fn)
        return p.get(sect, key)

    def load(self, fn=None, key=None):
        """Loads rc data from file.

        Rc data is obtained from the given file (``rc.yaml`` by default) and
        loaded into the given key (no key by default). This method collects
        rc files from :attr:`etc_dir`, the host directory and the environment
        directory.

        E.g. if you are on host 'foo-host' in environment 'bar-env' and want to
        load 'rcbaz.yaml', this method collects:

        1. etc/rcbaz.yaml
        2. etc/rcbazsecrets.yaml (if exists)
        3. etc/foo-host/rcbaz.yaml (if exists)
        4. etc/foo-host/rcbazsecrets.yaml (if exists)
        5. etc/foo-host/bar-env/rcbaz.yaml (if exists)
        6. etc/foo-host/bar-env/rcbazsecrets.yaml (if exists)

        :param fn: Name of rc file without path, but including extention.
        :param key: Loaded data is stored with this key
        """
        if fn is None:
            fn = 'rc.yaml'

        # Main rc file must exist
        fullfn = os.path.join(self.etc_dir, fn)
        self.load_file(fullfn, key, allow_empty=False)
        # Optional host rc
        fullfn = os.path.join(self.etc_dir, self.host, fn)
        try:
            self.load_file(fullfn, key, allow_empty=True)
        except IOError as exc:
            if self.debug:
                print(str(exc))
        # Optional environment rc
        if self.environment != self.__class__.NO_ENVIRONMENT:
            fullfn = os.path.join(self.etc_dir, self.host, self.environment, fn)
            try:
                self.load_file(fullfn, key, allow_empty=True)
            except IOError as exc:
                if self.debug:
                    print(str(exc))
        
        self.resolve_references()
        self.expand_these(keys=None, here=self.root_dir, root_dir=self.root_dir)

    def load_file(self, fn, key, allow_empty=False):
        """Loads given file and its corresponding secrets file

        A missing file throws an IOError
        A missing secrets file is silently ignored.
        Name of secrets file is given name appended with 'secrets', e.g.
        rc.yaml       -> rcsecrets.yaml
        myconfig.yaml -> myconfigsecrets.yaml
        
        :param fn: Full name of rc file (path, name and extention).
        :param key: Loaded data is stored with this key
        :param allow_empty: Existing rc file may be empty
        """
        # Load given file
        _, self._ext = os.path.splitext(fn)
        if self.debug: print("Loading rc into key '{0}' from file '{1}'".format(key, fn))
        stream = open(fn, 'rb')
        dd = load(stream)
        if dd:
            if key is None:
                self.data = dict(self.data, **dd)
            else:
                if key not in self.data:
                    self.data[key] = {}
                self.data[key] = dict(self.data[key], **dd)
        else:
            if allow_empty:
                if self.debug: print("WARNING: File is empty!")
            else:
                raise RcError("Rc file is empty: '{0}'".format(fn))
        # Try to load secrets file
        fn = fn.replace(self._ext, 'secrets'+self._ext)
        if self.debug: print("Loading rc secrets into key '{0}' from file '{1}'".format(key, fn))
        try:
            stream = open(fn, 'rb')
            dd = load(stream)
        except IOError as exc:
            if self.debug:
                print(str(exc))
            else:
                pass
        else:
            if dd:
                if key is None:
                    self.data.update(**dd)
                else:
                    if key not in self.data:
                        self.data[key] = {}
                    self.data[key].update(**dd)
            else:
                if self.debug: print("WARNING: File is empty!")

    def resolve_references(self):
        refconf = {}
        for k, v in self.data.items():
            m = self._re_ref_node.match(k)
            if m is None: continue
            prefix     = m.group('prefix')
            infix      = m.group('infix')
            ref_prefix = v + '.'
            lrp = len(ref_prefix)
            for ref_k, ref_v in self.data.items():
                if not ref_k.startswith(ref_prefix): continue
                ref_suffix = ref_k[lrp:]
                refconf[prefix + infix + '.' + ref_suffix] = ref_v
        self.data.update(refconf)

    def expand_these(self, keys=None, **kw):
        """Expands format variables in values with given data.

        On loading rc data, values that contain ``{here}`` and ``{root_dir}``
        are formatted with :attr:`root_dir`.

        :param keys: List of keys to expand. If empty, check all keys.
        :param kw: Keywords are passed to Python's ``str.format()``
        """
        if not keys:
            keys = self.data.keys()
        for k in keys:
            try:
                if isinstance(self.data[k], str):
                    self.data[k] = self.data[k].format(**kw)
            except KeyError:
                pass

    def g(self, key, defval=None):
        """Returns value of given key, or default value.
           If default value is not given and key is not found, raises KeyError
        """
        try:
            v = self.data[key]
        except KeyError as e:
            if defval is None:
                raise e
            else:
                v = defval
        return v

    def s(self, key, v):
        """Sets value for given key
           If key was already present, returns old value, else returns None.
        """
        try:
            ov = self.data[key]
        except KeyError:
            ov = None
        self.data[key] = v
        return ov

    def get_dir(self, key, defval=None):
        """Returned value expands '{here}' to root dir.
        """
        d = self.g(key, defval)
        return d.format(here=self.root_dir)

    def get_these(self, prefix):
        """Returns all rc nodes which start with prefix.
        """
        if not prefix.endswith('.'): prefix += '.'
        l = len(prefix)
        conf = {}
        for k, v in self.data.items():
            if k.startswith(prefix):
                conf[k[l:]] = v
        return conf

    def dump(self, prettyprinter=None):
        if not prettyprinter:
            import pprint
            prettyprinter = pprint.PrettyPrinter(indent=4)
        print('{0:=^78}'.format('[ RC DUMP ]'))
        prettyprinter.pprint(self.data)

    def logger_rc_filename(self):
        d = self.etc_dir
        f = 'rclogger'
        fn = os.path.join(d, self.host, f)
        if os.path.exists(fn):
            return fn
        fn = os.path.join(d, f)
        if os.path.exists(fn):
            return fn
        raise RcError("No rc file for loggers found")


if __name__ == '__main__':
    import pprint

    pp = pprint.PrettyPrinter(indent=4)
    
    rc = Rc()
    rc.load()

    rc.dump()

