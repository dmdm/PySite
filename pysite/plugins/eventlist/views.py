# -*- coding: utf-8 -*-

from pyramid.view import view_config
import logging

import pysite.resmgr

L = logging.getLogger('PySite')


@view_config(
    name='',
    context=pysite.plugins.eventlist.models.Node,
    renderer='pysite:plugins/events/templates/index.mako',
    permission='admin'
)
def index(context, request):
    return dict()


