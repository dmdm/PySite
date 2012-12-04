# -*- coding: utf-8 -*-

from pyramid.view import view_config
import logging

import pysite.resmgr

L = logging.getLogger('PySite')


@view_config(
    name='',
    context=pysite.resmgr.Root,
    renderer='pysite:templates/index.mako',
)
def index(context, request):
    return dict()


