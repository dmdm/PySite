# coding: utf-8

import babel
import babel.support
from pyramid.view import view_defaults
from pyramid.view import view_config
from pyramid.response import Response
from pyramid.httpexceptions import HTTPFound
from pyramid.i18n import get_locale_name

import pysite.resmgr
from pysite.sitemgr.page import Page


@view_defaults(context=pysite.sitemgr.models.Sites)
class SitesView(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(
        name=''
        , renderer='pysite:sitemgr/templates/index.mako'
    )
    @view_config(
        name='view'
        , renderer='pysite:sitemgr/templates/index.mako'
    )
    def view(self):
        return dict()

    # Add more view methods to manage sites here


@view_defaults(context=pysite.sitemgr.models.Site)
class SiteView(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config()
    @view_config(name='view')
    def view(self):
        return HTTPFound(self.request.resource_url(
            self.context, "index"))

    # Add more view methods to manage this site here


@view_defaults(context=pysite.sitemgr.models.Page)
class PageView(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config()
    @view_config(name='view')
    def view(self):
        page = Page(self.context, self.request)
        self._init_plugins(page)
        self._init_i18n(page)
        return Response(page.get_page())

    # Add more view methods to manage this page here
    

    def _init_i18n(self, page):
        locale_name = get_locale_name(self.request)
        page.jjglobals['bfmt'] = babel.support.Format(locale_name)

    def _init_plugins(self, page):
        plugins = {}
        # TODO Make this dynamic
        import pysite.plugins.eventlist as pluginmodule
        plugins[pluginmodule.NAME] = pluginmodule.request_factory(
            self.context.site
            , self.context
            , self.request
        )
        page.jjglobals['plugins'] = plugins
