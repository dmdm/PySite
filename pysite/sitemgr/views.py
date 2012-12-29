# coding: utf-8

import re
import os
import babel
import babel.support
from pyramid.view import view_defaults, view_config
from pyramid.response import Response
from pyramid.httpexceptions import HTTPFound
import pyramid.i18n
from pyramid.security import has_permission

import pysite.sitemgr.models
from pysite.sitemgr.page import Page
import pysite.lib
from pysite.sitemgr.replacer import Replacer


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



ALOHA_LOAD = """
<!-- BEGIN INJECTION aloha -->
<link rel="stylesheet" href="{aloha_css_url}" id="aloha-style-include" type="text/css">
<script src="{require_js_url}"></script>
<script src="{jquery_js_url}"></script>
<script src="{aloha_js_url}" data-aloha-plugins="{plugins}"></script>
<script src="{pysite_aloha_js_url}"></script>
<!-- END INJECTION aloha -->
</head>
"""

ALOHA_START = """
<!-- BEGIN INJECTION aloha -->
<script type="text/javascript">
Aloha.ready( function() {
    pysite_aloha('%USERNAME%', '%LOGOUT_URL%', '%SAVE_URL%', '%SELECTOR%', '%GUI_TOKEN%');
});
</script>
<!-- END INJECTION aloha -->
</body>
"""

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
        html = page.get_page()
        if has_permission('manage_files', self.context, self.request):
            html = self._inject_aloha(html)
        return Response(html)

    # Add more view methods to manage this page here
    @view_config(
        name='xhr_save_aloha',
        permission='manage_files',
        renderer='json'
    )
    def xhr_save_aloha(self):
        log = pysite.lib.StatusResp()
        fn = os.path.join(self.context.dir_, self.context.__name__) \
            + '.jinja2'
        r = Replacer()
        try:
            r.load_page(fn)
            s = r.replace(self.request.POST)
            with open(fn, 'w', encoding='utf-8') as fh:
                fh.write(s)
            log.ok('Saved.')
        except OSError as exc:
            log.error(str(exc))
        return log.resp

    def _inject_aloha(self, html):
        plugins = [
            'common/align',
            'common/block',
            'common/dom-to-xhtml',
            'common/format',
            'common/highlighteditables',
            'common/image',
            'common/link',
            'common/list',
            'common/paste',
            'common/table',
            'common/ui',
            'common/undo',
            'extra/metaview'
        ]
        aloha_css_url = self.request.static_url('pysite:static/app/libs/aloha/css/aloha.css')
        pysite_aloha_js_url = self.request.static_url('pysite:static/app/pysite_aloha.js')
        aloha_js_url = self.request.static_url('pysite:static/app/libs/aloha/lib/aloha.js')
        require_js_url = self.request.static_url('pysite:static/app/libs/aloha/lib/require.js')
        jquery_js_url = self.request.static_url('pysite:static/app/libs/aloha/lib/vendor/jquery-1.7.2.js')
        html = re.sub(r'</head\s*>',
            ALOHA_LOAD.format(
                pysite_aloha_js_url=pysite_aloha_js_url,
                aloha_js_url=aloha_js_url,
                aloha_css_url=aloha_css_url,
                require_js_url=require_js_url,
                jquery_js_url=jquery_js_url,
                plugins=",".join(plugins)
            ),
            html,
            flags=re.I
        )
        
        logout_url = self.request.resource_url(self.context.site, '@@logout')
        save_url = self.request.resource_url(self.context, '@@xhr_save_aloha')
        selector = '.editable'
        html = re.sub(r'</body\s*>',
            ALOHA_START.replace('%SELECTOR%', selector).replace(
                '%USERNAME%', self.request.user.display_name).replace(
                '%LOGOUT_URL%', logout_url).replace(
                '%SAVE_URL%', save_url).replace(
                '%GUI_TOKEN%', self.request.session.get_csrf_token().decode('utf-8')),
            html,
            flags=re.I
        )
        return html

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
