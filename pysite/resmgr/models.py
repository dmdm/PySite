# coding: utf-8


from pyramid.security import (
    Allow,
)
from pysite.resmgr.abstractmodels import Node
import pysite.plugins.models

class Root(Node):
    @property
    def title(self):
        return "Root"


class Sys(Node):
    __name__ = '__sys__'
    __acl__ = [
        (Allow, 'r:wheel', 'admin')
        , (Allow, 'r:wheel', 'plugins')
    ]

    def __init__(self, parent):
        super().__init__(parent)
        self['plugins'] = pysite.plugins.models.Node(self)
    
    @property
    def title(self):
        return "System"

