# coding: utf-8

"""
This module contains the SiteManager's nodes for the resource tree.

Node `/sites` is the root of the SiteManager. The :mod:`~.pysite.resmgr`
places it into the resource tree. Its children are the configured sites, which
are loaded dynamically.

Node `/sites/www.example.com` is the node of a configured site. Its
dynamically loaded children are the pages of this site.

Node `/sites/www.example.com/index` is the node of a page. It may have
subpages as its children or be a leaf node.

"""

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
        fn = os.path.normpath(os.path.join(dir_, '..', name + '.yaml'))
        if not os.path.exists(fn):
            msg = "Missing config file for site '{0}:{1}'".format(name, fn)
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

    @property
    def title(self):
        return "Sites"



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
            # Safe load user settings!
            rc = yaml.safe_load(fh)
        if rc:
            self.rc.update(rc)
        # Load master settings
        fn = os.path.normpath(os.path.join(dir_, '..', name + '.yaml'))
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

    @property
    def title(self):
        t = self.rc.get('title', None)
        if t:
            return t
        t = self.master_rc.get('title', None)
        if t:
            return t
        return self.__name__



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
        # If this page has no title set, get the one of the site
        # (if the site has one, that is)
        if not self.rc.get('title', None):
            t = site.rc.get('title', None)
            if t:
                self.rc['title'] = t

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

    @property
    def title(self):
        t = self.rc.get('title', None)
        if t:
            return t
        return self.__name__
