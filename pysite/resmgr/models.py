# coding: utf-8


from pyramid.security import (
    Allow,
    ALL_PERMISSIONS
)
import pysite.lib
import pysite.plugins.models
import pysite.sitemgr.models
import pysite.vmailmgr.models
import pysite.authmgr.models


class Root(pysite.lib.BaseNode):
    __acl__ = [
        (Allow, 'r:wheel', ALL_PERMISSIONS)
    ]
    def __init__(self, parent):
        super().__init__(parent)
        self._title = "Root"
        self['sites'] = pysite.sitemgr.models.Sites(self)
        self['__sys__'] = Sys(self)


class Sys(pysite.lib.BaseNode):
    __name__ = '__sys__'

    def __init__(self, parent):
        super().__init__(parent)
        self._title = "System"
        self['plugins'] = pysite.plugins.models.Node(self)
        self['vmailmgr'] = pysite.vmailmgr.models.Node(self)
        self['authmgr'] = pysite.authmgr.models.Node(self)
