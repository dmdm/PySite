# -*- coding: utf-8 -*-

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound
from pyramid.security import (
    remember
    , forget
    , NO_PERMISSION_REQUIRED
)

import pysite.authmgr.models


@view_defaults(
    context=pysite.authmgr.models.Node,
    permission='manage_auth'
)
class UsrMgrView(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(
        name='',
        renderer='pysite:authmgr/templates/index.mako',
    )
    def index(self):
        return dict()


@view_config(
    name='login',
    #context=pysite.sitemgr.models.Site,
    renderer='pysite:authmgr/templates/login.mako',
    permission=NO_PERMISSION_REQUIRED
)
def login(context, request):
    login_url = request.resource_url(context, '@@login')
    try:
        referrer = request.session.pop_flash(queue='login_referrer')[0]
    except IndexError:
        referrer = request.url
    if referrer == login_url:
        # never use the login form itself as came_from
        referrer = request.resource_url(context, 'index')
    came_from = request.params.get('came_from', referrer)

    login = ''
    pwd = ''
    msg = ''
    if 'submit' in request.POST:
        login = request.POST['login']
        pwd = request.POST['pwd']
        if request.user.login(login=login, pwd=pwd):
            headers = remember(request, request.user.principal)
            request.session.flash(dict(kind="info",text='User {0} logged in'.format(request.user.display_name)))
            return HTTPFound(location=came_from, headers=headers)
        else:
            msg = "Wrong credentials!"
            request.session.flash(dict(kind="error", text=msg))

    return dict(login=login, pwd=pwd, came_from=came_from, msg=msg, url=login_url)


@view_config(
    name='logout',
    #context=pysite.sitemgr.models.Site,
    permission=NO_PERMISSION_REQUIRED
)
def logout(context, request):
    # Must get current user's name before he logs out
    request.user.logout()
    headers = forget(request)
    return HTTPFound(location=request.resource_url(context),
                     headers=headers)

