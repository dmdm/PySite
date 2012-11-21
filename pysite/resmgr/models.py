# coding: utf-8

from pyramid.security import (
    Allow,
)


class Node(dict):
    __parent__ = None
    __name__   = None
    __acl__    = []

    def __init__(self, parent):
        self.__parent__ = parent

    def __setitem__(self, name, other):
        other.__parent__ = self
        other.__name__   = name
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

class Root(Node):
    @property
    def title(self):
        return "Root"

class Sys(Node):
    __name__ = '__sys__'
    __acl__ = [
        (Allow, 'r:wheel', 'admin')
        , (Allow, 'r:wheel', 'calendar')
    ]

    def __init__(self, parent):
        super().__init__(parent)
        self._init_plugins()

    def _init_plugins(self):
        # TODO Make this dynamic
        import pysite.plugins.calendar.models
        self['calendar'] = pysite.plugins.calendar.models.Node(self)
    
    @property
    def title(self):
        return "System"


