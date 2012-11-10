# coding: utf-8

from pyramid.security import (
    Allow,
)

from pysite.resmgr.models import (Root, Sys)
import pysite.sitemgr.models


root = Root(None)
root.__acl__ = [
    (Allow, 'r:wheel', 'admin')
    , (Allow, 'r:wheel', 'manage_files')
]
root['__sys__'] = Sys(root)
root['sites'] = pysite.sitemgr.models.Sites(root)


def root_factory(request):
    return root

