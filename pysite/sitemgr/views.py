# coding: utf-8

import string
import re
import os
import babel
import babel.support
import urllib.parse
import sqlite3
from pyramid.view import view_defaults, view_config
from pyramid.response import Response
from pyramid.httpexceptions import HTTPFound
import pyramid.i18n
from pyramid.security import has_permission

import pysite.sitemgr.models
from pysite.sitemgr.page import Page
import pysite.lib
from pysite.lib import safepath
from pysite.sitemgr.replacer import Replacer
from pysite.sitemgr.cache import Cache


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
<link rel="stylesheet" href="{aloha_css_url}" id="aloha-style-include"
    type="text/css">
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
            , filemgr_url: '$FILEMGR_URL'
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
        _init_plugins(self.context, self.request, page)
        _init_i18n(self.context, self.request, page)
        dir_ = self.context.dir_.replace(
            self.context.site.dir_, '').lstrip(os.path.sep)
        fn = os.path.join(dir_,
            self.context.__name__) + '.jinja2'
        html = page.get_page(fn)
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
        log = pysite.lib.JsonResp()
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
                'pysite:static/app/libs/jquery/ui/themes/'
                'humanity/jquery-ui.css'),
            pnotify_css_url=self.request.static_url(
                'pysite:static/app/libs/jquery/ui/pnotify/'
                'jquery.pnotify.default.css'),
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
        hash_ = finder.default_volume.encode(path)

        data = dict(
            GUI_TOKEN=self.request.session.get_csrf_token().decode('utf-8'),
            USERNAME=self.request.user.display_name,
            LOGOUT_URL=self.request.resource_url(self.context.site,
                '@@logout'),
            SAVE_URL=self.request.resource_url(self.context,
                '@@xhr_save_content'),
            SOURCE_URL=self.request.resource_url(self.context.site,
                '@@editor'),
            FILEMGR_URL=self.request.resource_url(self.context.site,
                '@@filemgr'),
            MIME='text/html',
            FILENAME=filename,
            HASH=hash_,
            SELECTOR='.editable'
        )
        wysiwyg_start = string.Template(WYSIWYG_START).substitute(data)
        html = re.sub(r'</body\s*>', wysiwyg_start, html, flags=re.I)
        return html


@view_defaults(context=pysite.sitemgr.models.Blog)
class BlogView(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request
        dsn = os.path.join(context.site.dir_, 'cache', 'blog', 'cache.sqlite3')
        self.cache = Cache(dsn, {})

    @view_config()
    @view_config(name='view')
    def view(self):
        self._sp = list(map(urllib.parse.unquote, self.context.slugparts))
        self._page = Page(self.context, self.request)
        self._page.jjglobals['authors'] = self.cache.list_authors()
        self._page.jjglobals['categories'] = self.cache.list_categories()
        self._page.jjglobals['tags'] = self.cache.list_tags()
        _init_plugins(self.context, self.request, self._page)
        _init_i18n(self.context, self.request, self._page)
        if self._sp[0] == 'index':
            return self._view_index()
        elif self._sp[0] == 'author':
            return self._view_author()
        elif self._sp[0] == 'category':
            return self._view_category()
        elif self._sp[0] == 'tag':
            return self._view_tag()
        else:
            return self._view_article()

    def _build_prev_next_links(self, sp):
        n = int(sp[-1])
        # prev
        if n <= 1:
            link_prev = None
        else:
            sp[-1] = n - 1
            link_prev = self._page.blog(['/'] + sp)
        # next
        sp[-1] = n + 1
        link_next = self._page.blog(['/'] + sp)
        return (link_prev, link_next)

    def _view_index(self):
        if len(self._sp) == 1:
            self._sp.append('1')
        n = int(self._sp[1])
        data = self.cache.get_index_page(n)
        self._render_data(data)
        fn = os.path.join(self.context.site.rc['blog.theme'],
            'index_page.jinja2')
        link_prev, link_next = self._build_prev_next_links(self._sp[:])
        html = self._page.get_page(fn, jjglobals={
            'data': data,
            'index_kind': 'Index',
            'index_name': None,
            'index_page': n,
            'link_prev': link_prev,
            'link_next': link_next
        })
        return Response(html)

    def _view_author(self):
        if len(self._sp) == 1:
            data = self.cache.list_authors()
            fn = os.path.join(safepath(self.context.site.rc['blog.theme']),
                'list_page.jinja2')
            html = self._page.get_page(fn, jjglobals={
                'data': data,
                'list_kind': 'Authors',
                'url_prefix': 'author/'
            })
            return Response(html)
        else:
            try:
                n = int(self._sp[-1])
            except ValueError:
                self._sp.append('1')
                n = 1
            author = '/'.join(self._sp[1:-1])
            data = self.cache.get_author_page(author, n)
            self._render_data(data)
            fn = os.path.join(safepath(self.context.site.rc['blog.theme']),
                'index_page.jinja2')
            link_prev, link_next = self._build_prev_next_links(self._sp[:])
            html = self._page.get_page(fn, jjglobals={
                'data': data,
                'index_kind': 'Author',
                'index_name': author,
                'index_page': n,
                'link_prev': link_prev,
                'link_next': link_next
            })
            return Response(html)

    def _view_category(self):
        if len(self._sp) == 1:
            data = self.cache.list_categories()
            fn = os.path.join(safepath(self.context.site.rc['blog.theme']),
                'list_page.jinja2')
            html = self._page.get_page(fn, jjglobals={
                'data': data,
                'list_kind': 'Categories',
                'url_prefix': 'category/'
            })
            return Response(html)
        else:
            try:
                n = int(self._sp[-1])
            except ValueError:
                self._sp.append('1')
                n = 1
            category = '/'.join(self._sp[1:-1])
            data = self.cache.get_category_page(category, n)
            self._render_data(data)
            fn = os.path.join(safepath(self.context.site.rc['blog.theme']),
                'index_page.jinja2')
            link_prev, link_next = self._build_prev_next_links(self._sp[:])
            html = self._page.get_page(fn, jjglobals={
                'data': data,
                'index_kind': 'Category',
                'index_name': category,
                'index_page': n,
                'link_prev': link_prev,
                'link_next': link_next
            })
            return Response(html)

    def _view_tag(self):
        if len(self._sp) == 1:
            data = self.cache.list_tags()
            fn = os.path.join(safepath(self.context.site.rc['blog.theme']),
                'list_page.jinja2')
            html = self._page.get_page(fn, jjglobals={
                'data': data,
                'list_kind': 'Tags',
                'url_prefix': 'tag/'
            })
            return Response(html)
        else:
            try:
                n = int(self._sp[-1])
            except ValueError:
                self._sp.append('1')
                n = 1
            tag = '/'.join(self._sp[1:-1])
            data = self.cache.get_tag_page(tag, n)
            self._render_data(data)
            fn = os.path.join(safepath(self.context.site.rc['blog.theme']),
                'index_page.jinja2')
            link_prev, link_next = self._build_prev_next_links(self._sp[:])
            html = self._page.get_page(fn, jjglobals={
                'data': data,
                'index_kind': 'Tag',
                'index_name': tag,
                'index_page': n,
                'link_prev': link_prev,
                'link_next': link_next
            })
            return Response(html)

    def _view_article(self):
        data = self.cache.get_article_by_slugparts(self._sp)
        self._render_data(data)
        fn = os.path.join(safepath(self.context.site.rc['blog.theme']),
            'article.jinja2')
        html = self._page.get_page(fn, jjglobals={'data': data})
        return Response(html)

    def _render_data(self, data):
        if isinstance(data, dict):
            # Render only the body, the summary is not necessary
            data['body'] = self._page.render_from_string(data['body'])
        else:
            for it in data:
                it['meta']['summary'] = self._page.render_from_string(
                    it['meta']['summary'])


def _init_i18n(context, request, page):
    locale = _negotiate_locale(context, request)
    page.jjglobals['locale'] = locale
    page.jjglobals['bfmt'] = babel.support.Format(locale.language)


def _negotiate_locale(context, request):
    # Fetch the configured list of available languages.
    avail_languages = context.site.rc.get(
        'i18n.avail_languages', None)

    # All languages are allowed
    if not avail_languages or '*' in avail_languages:
        avail_languages = babel.localedata.locale_identifiers()

    # Let Pyramid find the explicitly set locale via '_LOCALE_'.
    locale_name = pyramid.i18n.default_locale_negotiator(request)
    if locale_name:
        loc = babel.Locale.negotiate([locale_name], avail_languages)
        if loc:
            return loc
    # If no '_LOCALE_' was set, or the given one is not available,
    # get locale from client's browser setting.
    locale_name = request.accept_language.best_match(avail_languages)
    if locale_name:
        loc = babel.Locale.negotiate([locale_name], avail_languages)
        if loc:
            return loc
    # Eww, even that did not find a matching locale. Use the default, then.
    locale_name = context.rc.get('i18n.default_language', 'en')
    loc = babel.Locale.negotiate([locale_name], avail_languages)
    if not loc:
        loc = babel.Locale.parse('en')
    return loc


def _init_plugins(context, request, page):
    plugins = {}
    # TODO Make this dynamic
    import pysite.plugins.eventlist as pluginmodule
    plugins[pluginmodule.NAME] = pluginmodule.request_factory(
        context.site,
        context,
        request
    )
    page.jjglobals['plugins'] = plugins
