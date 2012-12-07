# -*- coding: utf-8 -*-

from pysite.resmgr import abstractmodels

class Node(abstractmodels.Node):
    __name__ = 'eventlist'

    def __init__(self, parent):
        self.__parent__ = parent
        self._title = "Eventlist"
