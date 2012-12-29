# coding: utf-8

import string
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



WYSIWYG_LOAD = """
<!-- BEGIN INJECTION -->
<link rel="stylesheet" href="{jqui_css_url}">
<link rel="stylesheet" href="{pnotify_css_url}">
<link rel="stylesheet" href="{aloha_css_url}" id="aloha-style-include" type="text/css">
<link rel="stylesheet" href="{wysiwyg_css_url}">

<script>
var require = {{
      baseUrl: '{base_url}'
    , deps: [
        '{plugins_js_url}'
    ]
    , paths: {{
          'jquery': 'libs/jquery/jquery'
        , 'ui':     'libs/jquery/ui'
        , 'requirejs': 'libs/aloha/lib'
    }}
    , shim: {{
          'ui/jquery-ui':              ['jquery']
        , 'libs/jstorage':             ['jquery']
        , 'ui/pnotify/jquery.pnotify': ['ui/jquery-ui']
    }}
    , waitSeconds: 15
}};
</script>
<script src="{require_js_url}"></script>
<script src="{aloha_js_url}" data-aloha-plugins="{plugins}"></script>
<!-- END INJECTION -->
</head>
"""

WYSIWYG_START = """
<!-- BEGIN INJECTION -->
<script type="text/javascript">
require(['requirejs/domReady!', 'jquery', 'pym', 'pym.editor.wysiwyg'],
function(doc,                   $$,        PYM) {
    PYM.init({
        gui_token: '$GUI_TOKEN'
    });
    Aloha.ready( function() {
        PYM.editor.wysiwyg.init({
            username: '$USERNAME'
            , logout_url: '$LOGOUT_URL'
            , save_url: '$SAVE_URL'
            , source_url: '$SOURCE_URL'
            , selector: '$SELECTOR'
            , mime: '$MIME'
            , filename: '$FILENAME'
            , hash: '$HASH'
        });
    });
});
</script>
<!-- END INJECTION -->
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
            html = self._inject_wysiwyg(html)
        return Response(html)

    # Add more view methods to manage this page here
    @view_config(
        name='xhr_save_content',
        permission='manage_files',
        renderer='json'
    )
    def xhr_save_content(self):
        log = pysite.lib.StatusResp()
        fn = os.path.join(self.context.dir_, self.context.__name__) \
            + '.jinja2'
        r = Replacer()
        try:
            r.load_page(fn)
            s = r.replace(self.request.POST)
            # TODO   Check fs quota!!! XXX
            with open(fn, 'w', encoding='utf-8') as fh:
                fh.write(s)
            log.ok('Saved.')
        except OSError as exc:
            log.error(str(exc))
        return log.resp

    def _inject_wysiwyg(self, html):
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
        data = dict(
            aloha_css_url=self.request.static_url(
                'pysite:static/app/libs/aloha/css/aloha.css'),
            jqui_css_url=self.request.static_url(
                'pysite:static/app/libs/jquery/ui/themes/humanity/jquery-ui.css'),
            pnotify_css_url=self.request.static_url(
                'pysite:static/app/libs/jquery/ui/pnotify/jquery.pnotify.default.css'),
            wysiwyg_css_url=self.request.static_url(
                'pysite:static/css/pym.editor.wysiwyg.css'),
            base_url=self.request.static_url(
                'pysite:static/app'),
            plugins_js_url=self.request.static_url(
                'pysite:static/app/libs/plugins.js'),
            require_js_url=self.request.static_url(
                'pysite:static/app/libs/aloha/lib/require.js'),
            aloha_js_url=self.request.static_url(
                'pysite:static/app/libs/aloha/lib/aloha.js'),
            plugins=','.join(plugins)
        )
        html = re.sub(r'</head\s*>',
            WYSIWYG_LOAD.format(**data),
            html,
            flags=re.I
        )

        from pysite.filemgr import create_finder
        finder = create_finder(self.context.site, self.request)
        filename = self.context.__name__ + '.jinja2'
        path = os.path.join(self.context.dir_, filename)
        print(list(finder.volumes.keys()))
        hash_ = finder.default_volume.encode(path)
        
        data = dict(
            GUI_TOKEN=self.request.session.get_csrf_token().decode('utf-8'),
            USERNAME=self.request.user.display_name,
            LOGOUT_URL=self.request.resource_url(self.context.site, '@@logout'),
            SAVE_URL=self.request.resource_url(self.context,
                '@@xhr_save_content'),
            SOURCE_URL=self.request.resource_url(self.context.site, '@@editor'),
            MIME='text/html',
            FILENAME=filename,
            HASH=hash_,
            SELECTOR='.editable'
        )
        wysiwyg_start = string.Template(WYSIWYG_START).substitute(data)
        html = re.sub(r'</body\s*>', wysiwyg_start, html, flags=re.I)
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
