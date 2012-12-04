# -*- coding: utf-8 -*-

from pyramid.view import view_config
import logging

import pysite.resmgr

L = logging.getLogger('PySite')


@view_config(
    name='',
    context=pysite.plugins.models.Node,
    renderer='pysite:plugins/templates/index.mako',
    permission='admin'
)
def index(context, request):
    return dict()


