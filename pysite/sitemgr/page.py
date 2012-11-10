# coding: utf-8

import os.path
import urllib.parse
import jinja2 as jj
from jinja2.sandbox import SandboxedEnvironment
import pyramid.traversal


class Sandbox(SandboxedEnvironment):
    pass #  TODO  Create a useful sandbox


class Page(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.jjenv = None
        self.jjglobals = dict(
            context=context
            , request=request
            , site=context.site.rc
            , page=context.rc
            , url=self.url
            , asset_url=self.asset_url
        )
        self.jjcontext = dict()
        self.jjtpl = None
        self.page = None
        self.tpldir = None
        # TODO Register any jjglobals from the requested plugins
        self.init_jinja()

    def get_page(self, jjglobals=None, jjcontext=None):
        self.load(jjglobals=jjglobals)
        self.render(jjcontext=jjcontext)
        return self.page

    def init_jinja(self):
        self.tpldir = os.path.join(self.context.site.dir_, 'content')
        self.jjenv = Sandbox(
            loader=jj.FileSystemLoader(self.tpldir, encoding='utf-8')
            , autoescape=True
            , auto_reload=True
        )

    def load(self, fn=None, jjglobals=None):
        if not fn:
            dir_ = self.context.dir_.replace(self.tpldir, '')
            fn = os.path.join(dir_,
                self.context.__name__) + '.jinja2'
        if jjglobals:
            self.jjglobals.update(jjglobals)
        self.jjtpl = self.jjenv.get_template(fn, globals=self.jjglobals)

    def render(self, jjcontext=None):
        if jjcontext:
            self.jjcontext.update(jjcontext)
        self.page = self.jjtpl.render(self.jjcontext)

    def url(self, path, **kw):
        tgtres = pyramid.traversal.find_resource(self.context.__parent__, path)
        return self.request.resource_url(tgtres, **kw)

    def asset_url(self, path, **kw):
        url = "/static-" + self.context.site.__name__ + '/' + path
        if '_query' in kw:
            url += '?' + urllib.parse.urlencode(kw['_query'], doseq=True)
        if '_anchor' in kw:
            url += '#' + kw['_anchor']
        return url
