# coding: utf-8


class Node(dict):
    __parent__ = None
    __name__   = None
    __acl__    = []

    def __init__(self, parent):
        self.__parent__ = parent
        self._title = None

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

    @property
    def title(self):
        return self._title if self._title else self.__name__

