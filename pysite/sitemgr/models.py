# coding: utf-8

from glob import glob
import os.path
import yaml
import logging
try:
    from yaml import CLoader as YamlLoader
except ImportError:
    from yaml import Loader as YamlLoader

import pyramid.security

from pysite.lib import validate_name


logger = logging.getLogger(__name__)


class Sites(object):
    __parent__ = None
    __name__   = "sites"
    __acl__    = []

    SITES_DIR = None
    """Directory where the sites are stored.
    This must be set during app startup!
    """

    def __init__(self, parent):
        self.__parent__ = parent

    def __getitem__(self, name):
        validate_name(name)
        dir_ = os.path.join(self.__class__.SITES_DIR, name)
        if not os.path.exists(dir_):
            msg = "Site not found: '{0}'".format(name)
            logger.error(msg)
            raise KeyError(msg)
        fn = os.path.realpath(os.path.join(dir_, '..', name + '.yaml'))
        if not os.path.exists(fn):
            msg = "Missing config file for site '{0}'".format(name)
            logger.error(msg)
            raise KeyError(msg)
        return Site(self, name, dir_)

    def __iter__(self):
        return [ os.path.basename(it)
            for it in glob(os.path.join(self.__class__.SITES_DIR, '*')) ]

    def keys(self):
        return self.__iter__()

    def __contains__(self, item):
        return item in self.__iter__()

    def __str__(self):
        s = self.__name__ if self.__name__ else '/'
        o = self.__parent__
        while o:
            s = (o.__name__ if o.__name__ else '') + '/' + s
            o = o.__parent__
        return str(type(self)).replace('>', ": '{}'>".format(s))


class Site(object):
    __parent__ = None
    __name__   = None
    __acl__    = []

    def __init__(self, parent, name, dir_):
        self.__parent__ = parent
        self.__name__ = name
        self.dir_ = dir_
        self.rc = dict()
        self.master_rc = dict()
        # Load user settings
        fn = os.path.join(dir_, 'rc.yaml')
        with open(fn, 'r', encoding='utf-8') as fh:
            rc = yaml.load(fh, YamlLoader)
        if rc:
            self.rc.update(rc)
        # Load master settings
        fn = os.path.join(dir_, '..', name + '.yaml')
        with open(fn, 'r', encoding='utf-8') as fh:
            rc = yaml.load(fh, YamlLoader)
        if rc:
            if 'acl' in rc:
                self._init_acl(rc['acl'])
                del rc['acl']
            self.master_rc.update(rc)

    def _init_acl(self, acl0):
        acl = []
        for ace0 in acl0:
            if 'deny'.startswith(ace0[0].lower()):
                perm = pyramid.security.Deny
            elif 'allow'.startswith(ace0[0].lower()):
                perm = pyramid.security.Allow
            else:
                raise Exception("Invalid permission: '{0}'".format(ace0[0]))
            acl.append( (perm, ace0[1], ace0[2]) )
        self.__acl__ = acl

    def __getitem__(self, name):
        # Access system nodes
        if name == '__sys__':
            # I expect my parent's parent to be root!
            node = self.__parent__.__parent__[name]
            # Since we're fetching the node from a different location,
            # we must advertise ourselves as parent to no break the lineage.
            node.__parent__ = self
            return node
        # Access files from current site
        validate_name(name)
        dir_ = os.path.join(self.dir_, 'content')
        fn = os.path.join(dir_, name) + '.yaml'
        if not os.path.exists(fn):
            raise KeyError("Page not found: '{0}'".format(name))
        return Page(self, self, name, dir_)

    def __iter__(self):
        return [ os.path.splitext(os.path.basename(it))[0]
            for it in glob(os.path.join(self.dir_, 'content', '*.yaml')) ]

    def keys(self):
        return self.__iter__()

    def __contains__(self, item):
        return item in self.__iter__()

    def __str__(self):
        s = self.__name__ if self.__name__ else '/'
        o = self.__parent__
        while o:
            s = (o.__name__ if o.__name__ else '') + '/' + s
            o = o.__parent__
        return str(type(self)).replace('>', ": '{}'>".format(s))


class Page(object):
    __parent__ = None
    __name__   = None
    __acl__    = []

    def __init__(self, parent, site, name, dir_):
        self.__parent__ = parent
        self.__name__ = name
        self.site = site
        self.dir_ = dir_
        fn = os.path.join(dir_, name) + '.yaml'
        with open(fn, 'r', encoding='utf-8') as fh:
            self.rc = yaml.load(fh, YamlLoader)

    def __getitem__(self, name):
        validate_name(name)
        dir_ = os.path.join(self.dir_, self.__name__)
        fn = os.path.join(dir_, name) + '.yaml'
        if not os.path.exists(fn):
            raise KeyError("Page not found: '{0}'".format(name))
        return Page(self, self.site, name, dir_)

    def __iter__(self):
        return [ os.path.splitext(os.path.basename(it))[0]
            for it in glob(os.path.join(self.dir_,
                self.__name__, '*.yaml')) ]

    def keys(self):
        return self.__iter__()

    def __contains__(self, item):
        return item in self.__iter__()

    def __str__(self):
        s = self.__name__ if self.__name__ else '/'
        o = self.__parent__
        while o:
            s = (o.__name__ if o.__name__ else '') + '/' + s
            o = o.__parent__
        return str(type(self)).replace('>', ": '{}'>".format(s))

