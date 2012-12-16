# coding: utf-8

import babel
import babel.support
from pyramid.view import view_defaults, view_config
from pyramid.response import Response
from pyramid.httpexceptions import HTTPFound
import pyramid.i18n

import pysite.sitemgr.models
from pysite.sitemgr.page import Page


@view_defaults(context=pysite.sitemgr.models.Sites)
class SitesView(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(
        name='',
        renderer='pysite:sitemgr/templates/index.mako'
    )
    @view_config(
        name='view',
        renderer='pysite:sitemgr/templates/index.mako'
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
        locale = self._negotiate_locale()
        page.jjglobals['locale'] = locale
        page.jjglobals['bfmt'] = babel.support.Format(locale.language)

    def _negotiate_locale(self):
        # Fetch the configured list of available languages.
        avail_languages = self.context.site.rc.get(
            'i18n.avail_languages', None)

        # All languages are allowed
        if not avail_languages or '*' in avail_languages:
            avail_languages = babel.localedata.locale_identifiers()

        # Let Pyramid find the explicitly set locale via '_LOCALE_'.
        locale_name = pyramid.i18n.default_locale_negotiator(self.request)
        if locale_name:
            loc = babel.Locale.negotiate([locale_name], avail_languages)
            if loc:
                return loc
        # If no '_LOCALE_' was set, or the given one is not available,
        # get locale from client's browser setting.
        locale_name = self.request.accept_language.best_match(avail_languages)
        if locale_name:
            loc = babel.Locale.negotiate([locale_name], avail_languages)
            if loc:
                return loc
        # Eww, even that did not find a matching locale. Use the default, then.
        locale_name = self.context.rc.get('i18n.default_language', 'en')
        loc = babel.Locale.negotiate([locale_name], avail_languages)
        if not loc:
            loc = babel.Locale.parse('en')
        return loc

    def _init_plugins(self, page):
        plugins = {}
        # TODO Make this dynamic
        import pysite.plugins.eventlist as pluginmodule
        plugins[pluginmodule.NAME] = pluginmodule.request_factory(
            self.context.site,
            self.context,
            self.request
        )
        page.jjglobals['plugins'] = plugins
