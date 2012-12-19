# coding: utf-8

import os.path
import urllib.parse
import jinja2 as jj
import jinja2.sandbox
import markupsafe
import pyramid.traversal

import pysite.security
import pysite.lib


class Sandbox(jinja2.sandbox.SandboxedEnvironment):
    pass  # TODO  Create a useful sandbox


class Page(object):
    """
    Loads and renders a page.

    This class facades creating a Jinja environment, loading the
    appropriate template for a given request and finally rendering the
    page.

    On creation, a page instance is initialised with a context and a request
    object from the current request. It also initialises a sandboxed
    environment for Jinja. A caller may override the default Jinja environment
    by setting attribute :attr:`jjenv`.

    The simplest task is to just render the page for the current request, e.g.
    inside a Pyramid view::

        @view_config(...)
        def view(context, request):
            page = Page(context, request)
            return Response(page.get_page())

    The rendering environment by default is a sandbox, and the following
    globals are available in a template:

    - `site`:    Contains the settings of the site.
      Usage: `{{ site.title }}`
    - `page`:    Contains the settings of the current page.
      Usage: `{{ page.keywords }}`
    - `url()`:   See :meth:`url`
    - `asset_url()`: See :meth:`asset_url`
    - 'load_config(): See :meth:`load_config`

    It also sets these options:

    - `autoescape` = True
    - `auto_reload` = True
    """

    def __init__(self, context, request):
        self.context = context
        """Context of current request"""
        self.request = request
        """Current request"""
        self.jjenv = None
        """Instance of a Jinja environment"""
        self.jjglobals = dict(
            site=context.site.rc,
            page=context.rc,
            url=self.url,
            asset_url=self.asset_url,
            load_config=self.load_config
        )
        """Dict of variables that will globally be available in a template"""
        self.jjcontext = dict()
        """Dict used for Jinja rendering context"""
        self.jjtpl = None
        """Instance of a loaded Jinja template"""
        self.page = None
        """Rendered page as string"""
        self.tpldir = None
        """Template directory for current request"""
        # TODO Register any jjglobals from the requested plugins
        self._init_jinja()

    def get_page(self, jjglobals=None, jjcontext=None):
        """
        Returns the rendered page for current request.

        This function is for convenience, as it just encapsulates calls to
        :func:`load()` and :func:`render()`.

        :param jjglobals: A dict with additional globals; passed to
            :meth:`load`.
        :param jjcontext: A dict with additional settings for the rendering
            context; passed to :meth:`render`.
        :returns: Rendered page as string.
        """
        self.load(jjglobals=jjglobals)
        self.render(jjcontext=jjcontext)
        return self.page

    def _init_jinja(self):
        site_dir = self.context.site.dir_
        self.tpldir = os.path.join(site_dir, 'content')
        self.jjenv = Sandbox(
            loader=jj.FileSystemLoader(site_dir, encoding='utf-8'),
            autoescape=True,
            auto_reload=True
        )
        self.jjenv.filters['markdown'] = \
            self.request.registry.pysite_markdown.convert

    def load(self, fn=None, jjglobals=None):
        """
        Loads a template.

        Populates attribute :attr:`jjtpl` with an instance of the Jinja
        template.

        :param fn: Filename of the template. If omitted, it is built according
            to the current request's context.
        :param jjglobals: A dict with additional globals to pass to the
            template.  If set, attribute :attr:`jjglobals` is updated by these.
        """
        if not fn:
            dir_ = self.context.dir_.replace(self.tpldir, '')
            fn = os.path.join(dir_, 'content',
                self.context.__name__) + '.jinja2'
        if jjglobals:
            self.jjglobals.update(jjglobals)
        try:
            self.jjtpl = self.jjenv.get_template(fn, globals=self.jjglobals)
        except jj.TemplateSyntaxError as exc:
            self.jjtpl = jj.Template("""<html>
            <head><title>Template Syntax Error</title></head>
            <body><h1>Template Syntax Error</h1>
            <p><strong>{message}</strong></p>
            <p>in template "{name}", line {lineno}</p>
            </body>
            </html>
            """.format(message=exc.message, name=exc.name, lineno=exc.lineno))
        except jj.TemplateError as exc:
            self.jjtpl = jj.Template("""<html>
            <head><title>Template Error</title></head>
            <body><h1>Template Error</h1><pre>{0}: {1}</pre></body>
            </html>
            """.format(markupsafe.escape(type(exc)), str(exc)))

    def render(self, jjcontext=None):
        """
        Renders current template.

        Stores rendered page as string in attribute :attr:`page`.

        :param jjcontext: Dict with additional settings for the render
            context. If set, attribute :attr:`jjcontext` is updated by these.
        """
        if jjcontext:
            self.jjcontext.update(jjcontext)
        try:
            self.page = self.jjtpl.render(self.jjcontext)
        except jj.TemplateError as exc:
            tpl = jj.Template("""<html>
                <head><title>Template Error</title></head>
                <body><h1>Template Error</h1><pre>{0}: {1}</pre></body>
                </html>
                """.format(markupsafe.escape(type(exc)), str(exc)))
            self.page = tpl.render(self.jjcontext)

    def url(self, path, **kw):
        """
        Returns absolute URL to another page.

        Determines `path`'s target resource and then calls current
        request's method `resource_url()` to create the URL. All
        optional keyword arguments are passed to `resource_url()`.

        Usage::

            <p>Go to <a href="{{ url("dir_1/dir_2/other_page") }}">
            other page</a></p>

        :param path: Relative path to another page, which is stored in site's
                     `content` directory.
        :returns: Absolute URL to another page
        """
        try:
            tgtres = pyramid.traversal.find_resource(self.context.__parent__, path)
        except KeyError:
            # Let the user type in URL to a page that does not yet exist,
            # but signal it.
            # If we would not catch this exception, the webserver would cry 500.
            return '#page-not-found'
        url = self.request.resource_url(tgtres, **kw)
        # Since we do not pass any element parts to resource_url(), the generated
        # URL will always end with '/'. If a query string or an anchor is appended,
        # the last '/' will trick the traversal to look for a subelement, which
        # does not exist. So we kill that last '/'.
        return pysite.lib.rreplace(url, '/', '', 1)

    def asset_url(self, path, query=None, anchor=None):
        """
        Returns URL to a static asset, e.g. CSS file.

        Assets are stored in the site's `assets` directory, which is published
        via a static route in Pyramid.

        Usage::

            <img src="{{ asset_url("img/grass-mud-horse2.jpg") }}">

        :param path: Path to a static asset, relative to the assets directory.
        :param query: Optional data to build a query string. Internally is
            passed to `urllib.parse.urlencode`.
        :param anchor: Optional an anchor name.
        :returns: Absolute URL to static asset

        .. todo:: Add a signal, so that plugins can hook into the creation
            of the static URL and trigger e.g. cimpilation of LESSCSS or
            sth. like this.

            If hook returns its generated URL, no more hooks shall be
            signaled. If hook returns None, the next hook is signaled.
            If all hooks returned None, the default generation takes place.
        """
        url = "/static-" + self.context.site.__name__ + '/' + path
        if query:
            url += '?' + urllib.parse.urlencode(query, doseq=True)
        if anchor:
            url += '#' + anchor
        return url

    def load_config(self, fn, encoding='utf-8'):
        """
        Loads a configuration file.
        
        YAML, JSON and INI format are supported.
        
        Usage::

            {% set data = load_config("test.yaml") %}
            {% for k, v in data.items() %}
                <div>Found key "{{k}}" with value "{{v}}".</div>
            {% endfor %}

        :param fn: Name of configuration file. Path may be relative or absolute
            within the site.
        :param encoding: Optional. Character set encoding of the configuration
            data.  Defaults to 'utf-8'.
        :returns: Loaded data structure, mostly list or dict.
        """
        return pysite.lib.load_site_config(self.context.dir_, fn, encoding)
