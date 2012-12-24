# -*- coding: utf-8 -*-

from pyramid.view import view_config, view_defaults
import pysite.vmailmgr.models


@view_defaults(
    context=pysite.vmailmgr.models.Node,
    permission='manage_vmail'
)
class VmailMgrView(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(
        name='',
        renderer='pysite:vmailmgr/templates/index.mako',
    )
    def index(self):
        return dict()
