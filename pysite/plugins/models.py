# -*- coding: utf-8 -*-

import pysite.lib

class Node(pysite.lib.BaseNode):
    __name__ = 'plugins'

    def __init__(self, parent):
        super().__init__(parent)
        self._title = "Plugins"
        # TODO Make this dynamic
        import pysite.plugins.eventlist.models
        self['eventlist'] = pysite.plugins.eventlist.models.Node(self)
