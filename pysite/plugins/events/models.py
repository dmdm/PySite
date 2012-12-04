# -*- coding: utf-8 -*-


class Node(object):
    __name__ = 'events'

    def __init__(self, parent):
        self.__parent__ = parent

    def __str__(self):
        s = self.__name__ if self.__name__ else '/'
        o = self.__parent__
        while o:
            s = (o.__name__ if o.__name__ else '') + '/' + s
            o = o.__parent__
        return str(type(self)).replace('>', ": '{}'>".format(s))

    @property
    def title(self):
        return "Events"
