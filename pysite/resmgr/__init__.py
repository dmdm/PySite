# coding: utf-8

from pysite.resmgr.models import Root


root = Root(None)


def root_factory(request):
    return root

