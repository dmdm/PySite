# -*- coding: utf-8 -*-

import os
import jinja2 as jj
import jinja2.sandbox
import markdown

from ext_assets import AssetsEnvironment, AssetsExtension


class Sandbox(jinja2.sandbox.SandboxedEnvironment):
    pass


class Renderer(object):
    def __init__(self):
        self.tpldir = None
        self.jjenv = None
        self.jjglobals = dict()
        self.jjcontext = dict()
        self.jjtpl = None
        self._init_jinja()

    def _init_jinja(self):
        if not self.tpldir:
            self.tpldir = os.path.dirname(__file__)
        self.jjenv = Sandbox(
            loader=jj.FileSystemLoader(self.tpldir, encoding='utf-8')
            , autoescape=True
            , auto_reload=True
            , extensions=[AssetsExtension]
        )
        self.jjenv.assets_environment = AssetsEnvironment()
        self.jjenv.filters['markdown'] = self._filter_markdown


    def get_page(self, jjglobals=None, jjcontext=None):
        self.load(jjglobals=jjglobals)
        self.render(jjcontext=jjcontext)
        return self.page

    def load(self, fn=None, jjglobals=None):
        if not fn:
            fn = os.path.join(self.tpldir, 'page.jinja2')
        if jjglobals:
            self.jjglobals.update(jjglobals)
        #import ipdb; ipdb.set_trace()
        self.jjtpl = self.jjenv.get_template(fn, globals=self.jjglobals)

    def render(self, jjcontext=None):
        if jjcontext:
            self.jjcontext.update(jjcontext)
        self.page = self.jjtpl.render(self.jjcontext)

    def _filter_markdown(self, text):
        extensions = [
            'abbr',
            'attr_list',
            'def_list',
            'fenced_code',
            'footnotes',
            'smart_strong',
            'tables',
            'codehilite',
            'sane_lists',
            'toc'
        ]
        extension_configs = dict()
        # We are calling markdown from a Jinja template which is intended to
        # contain user written HTML, so do not use safe_mode here to escape raw
        # HTML inside markdown.
        opts = dict(
            extensions=extensions,
            extension_configs=extension_configs,
            output_format='html5',
            safe_mode=False
        )
        # Instanciate Markdown once per application and re-use it in each request
        md = markdown.Markdown(**opts)
        return md.convert(text)


if __name__ == '__main__':
    r = Renderer()
    p = r.get_page()
    print(p)
