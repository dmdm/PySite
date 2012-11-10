# coding: utf-8

from pyramid.view import view_defaults
from pyramid.view import view_config
from pyramid.response import Response
from pyramid.httpexceptions import HTTPFound

import pysite.resmgr
from pysite.sitemgr.page import Page


@view_defaults(context=pysite.sitemgr.models.Sites)
class SitesView(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config()
    @view_config(name='view')
    def view(self):
        return Response('huhu')

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
        return Response(page.get_page())

    # Add more view methods to manage this page here
