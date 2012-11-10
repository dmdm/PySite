# -*- coding: utf-8 -*-

from pyramid.view import view_config
import logging

import pysite.resmgr

L = logging.getLogger('PySite')


@view_config(
    name='',
    context=pysite.plugins.calendar.models.Node,
    renderer='pysite:plugins/calendar/templates/index.mako',
    permission='calendar'
)
def index(context, request):
    return dict()


