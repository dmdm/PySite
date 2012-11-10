# -*- coding: utf-8 -*-

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.security import (
    remember
    , forget
    , NO_PERMISSION_REQUIRED
)

import pysite.sitemgr.models
import pysite.resmgr.models


@view_config(
    name='login',
    #context=pysite.sitemgr.models.Site,
    renderer='pysite:usrmgr/templates/login.mako',
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
            return HTTPFound(location=came_from, headers=headers)
        else:
            msg = "Wrong credentials!"

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

