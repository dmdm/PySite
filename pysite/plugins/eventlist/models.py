# -*- coding: utf-8 -*-

import pysite.lib

class Node(pysite.lib.BaseNode):
    __name__ = 'eventlist'

    def __init__(self, parent):
        self.__parent__ = parent
        self._title = "Eventlist"
