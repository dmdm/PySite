# coding: utf-8

import os.path
import urllib.parse
import jinja2 as jj
import jinja2.sandbox
import pyramid.traversal

import pysite.security

class Sandbox(jinja2.sandbox.SandboxedEnvironment):
    pass #  TODO  Create a useful sandbox


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

    The rendering environment by default is a sandbox, and the following globals
    are available in a template:

    - `site`:    Contains the settings of the site.
      Usage: `{{ site.title }}`
    - `page`:    Contains the settings of the current page.
      Usage: `{{ page.keywords }}`
    - `url()`:   See :meth:`url`
    - `asset_url()`: See :meth:`asset_url`

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
              site=context.site.rc
            , page=context.rc
            , url=self.url
            , asset_url=self.asset_url
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

        :param jjglobals: A dict with additional globals; passed to :meth:`load`.
        :param jjcontext: A dict with additional settings for the rendering
            context; passed to :meth:`render`.
        :returns: Rendered page as string.
        """
        self.load(jjglobals=jjglobals)
        self.render(jjcontext=jjcontext)
        return self.page

    def _init_jinja(self):
        self.tpldir = os.path.join(self.context.site.dir_, 'content')
        self.jjenv = Sandbox(
            loader=jj.FileSystemLoader(self.tpldir, encoding='utf-8')
            , autoescape=True
            , auto_reload=True
        )

    def load(self, fn=None, jjglobals=None):
        """
        Loads a template.

        Populates attribute :attr:`jjtpl` with an instance of the Jinja template.

        :param fn: Filename of the template. If omitted, it is built according
            to the current request's context.
        :param jjglobals: A dict with additional globals to pass to the template.
            If set, attribute :attr:`jjglobals` is updated by these.
        """
        if not fn:
            dir_ = self.context.dir_.replace(self.tpldir, '')
            fn = os.path.join(dir_,
                self.context.__name__) + '.jinja2'
        if jjglobals:
            self.jjglobals.update(jjglobals)
        self.jjtpl = self.jjenv.get_template(fn, globals=self.jjglobals)

    def render(self, jjcontext=None):
        """
        Renders current template.

        Stores rendered page as string in attribute :attr:`page`.

        :param jjcontext: Dict with additional settings for the render
            context. If set, attribute :attr:`jjcontext` is updated by these.
        """
        if jjcontext:
            self.jjcontext.update(jjcontext)
        self.page = self.jjtpl.render(self.jjcontext)

    def url(self, path, **kw):
        """
        Returns absolute URL to another page.

        Determines `path`'s target resource and then calls current
        request's method `resource_url()` to create the URL. All
        optional keyword arguments are passed to `resource_url()`.

        Usage::

            <p>Go to <a href="{{ url("dir_1/dir_2/other_page") }}">other page</a></p>

        :param path: Relative path to another page, which is stored in site's
                     `content` directory.
        :returns: Absolute URL to another page
        """
        tgtres = pyramid.traversal.find_resource(self.context.__parent__, path)
        return self.request.resource_url(tgtres, **kw)

    def asset_url(self, path, query=None, anchor=None):
        """
        Returns URL to a static asset, e.g. CSS file.

        Assets are stored in the site's `assets` directory, which is published
        via a static route in Pyramid.

        Usage::

            <img src="{{ asset_url("img/grass-mud-horse2.jpg") }}">

        :param path: Path to a static asset, relative to the assets directory.
        :param query: Optional data to build a query string. Internally is passed to
                      `urllib.parse.urlencode`.
        :param anchor: Optional an anchor name.
        :returns: Absolute URL to static asset
        """
        url = "/static-" + self.context.site.__name__ + '/' + path
        if query:
            url += '?' + urllib.parse.urlencode(query, doseq=True)
        if anchor:
            url += '#' + anchor
        return url
