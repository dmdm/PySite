# -*- coding: utf-8 -*-

from pysite.resmgr import abstractmodels

class Node(abstractmodels.Node):
    __name__ = 'plugins'

    def __init__(self, parent):
        super().__init__(parent)
        self._title = "Plugins"
        # TODO Make this dynamic
        import pysite.plugins.eventlist.models
        self['eventlist'] = pysite.plugins.eventlist.models.Node(self)
