# -*- coding: utf-8 -*-

from pyramid.view import view_config
import pysite.vmailmgr

@view_config(
    name='',
    context=pysite.vmailmgr.models.Node,
    renderer='pysite:vmailmgr/templates/index.mako',
    permission='manage_vmail'
)
def index(context, request):
    return dict()
