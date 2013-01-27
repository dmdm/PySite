# -*- coding: utf-8 -*-

from pyramid.view import view_config, view_defaults
from pyramid.response import Response
import os
import logging

from pym_elfinder.exceptions import FinderError
import pysite.sitemgr.models
from pysite.filemgr import create_finder
from pysite.sitemgr.cache import Cache
from pysite.sitemgr.blog import Blog
import pysite.lib


L = logging.getLogger('PySite')


@view_defaults(
    context=pysite.sitemgr.models.Site,
    permission='manage_files'
)
class FileMgrView(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request
        #dsn = ':memory:'
        dsn = os.path.join(context.dir_, 'cache', 'blog', 'cache.sqlite3')
        self.cache = Cache(dsn, {})
        self.blog = Blog(self.cache, {
            'site_dir': context.dir_
        })

    @view_config(
        name='filemgr',
        renderer='pysite:filemgr/templates/filemgr.mako',
    )
    def filemgr(self):
        logo_url = self.request.static_url('pysite:static/img/filemgr.png')
        logo_alt = 'FileManager'
        return dict(logo_url=logo_url, logo_alt=logo_alt)

    @view_config(
        name='xhr_filemgr',
        renderer='json',
    )
    def xhr_filemgr(self):
        cmd = ''
        cmd_args = dict()
        for k in self.request.params:
            if k == '_':
                continue
            if k == 'cmd':
                cmd = self.request.params[k]
            else:
                if k.endswith("[]"):
                    k2 = k.rstrip("[]")
                    cmd_args[k2] = self.request.params.getall(k)
                else:
                    cmd_args[k] = self.request.params[k]
        finder = create_finder(self.context, self.request)
        try:
            finder.run(cmd, cmd_args)
        except FinderError as e:
            L.exception(e)
            if e.status:
                self.request.response.status = e.status
        if 'file' in finder.response:
            resp = Response()
            resp.app_iter = finder.response['file']
            if finder.headers:
                for k, v in finder.headers.items():
                    resp.headers[k] = v
            return resp
        else:
            if finder.headers:
                for k, v in finder.headers.items():
                    self.request.response.headers[k] = v
            return finder.response

    @view_config(
        name='editor',
        renderer='pysite:filemgr/templates/editor.mako',
    )
    def editor(self):
        resp = dict(
            sassc_url=self.request.resource_url(
                self.context, '@@xhr_sassc'),
            blog_update_url=self.request.resource_url(
                self.context, '@@xhr_blog_update'),
            blog_rebuild_url=self.request.resource_url
                (self.context, '@@xhr_blog_rebuild')
        )
        return resp

    @view_config(
        name='xhr_blog_update',
        renderer='json',
    )
    def xhr_blog_update(self):
        resp = pysite.lib.JsonResp()
        self.blog.build(full=False)
        for e in self.blog.errors:
            resp.error(str(e))
        resp.ok('{0} file(s) updated.'.format(self.blog.done))
        return resp.resp

    @view_config(
        name='xhr_blog_rebuild',
        renderer='json',
    )
    def xhr_blog_rebuild(self):
        resp = pysite.lib.JsonResp()
        self.blog.build(full=True)
        for e in self.blog.errors:
            resp.error(str(e))
        resp.ok('{0} file(s) updated.'.format(self.blog.done))
        return resp.resp

    @view_config(
        name='xhr_sassc',
        renderer='json',
    )
    def xhr_sassc(self):
        # Context is Site
        site_dir = self.context.dir_
        rc = self.context.rc
        resp = pysite.lib.compile_sass(site_dir, rc)
        return resp.resp


_DEVEL_OPTS = {
    'debug': True,
    'roots': [
        dict(
            id="1",
            driver='pym_elfinder.volume.localfilesystem',
            path=os.path.abspath(os.path.realpath(os.path.join(
                            os.path.dirname(__file__), '..', '..', '..',
                            'Pym-elFinder',
                            'pym_elfinder_tests', 'fixtures', 'files'))),
            #startPath='../files/test/',
            #URL=dirname($_SERVER['PHP_SELF']) . '/../files/',
            # treeDeep=3,
            # alias='File system',
            mimeDetect='internal',
            #tmbPath='.tmb',
            utf8fix=True,
            #tmbCrop=False,
            #tmbBgColor='transparent',
            accessControl='access',
            acceptedName='/^[^\.].*$/',
            # tmbSize=128,
            attributes=[
                dict(
                    pattern='/\.js$/',
                    read=True,
                    write=False
                ),
                dict(
                    pattern='/^\/icons$/',
                    read=True,
                    write=False
                ),
                dict(
                    pattern='/^[^.].*$/',
                    read=True,
                    write=True
                )
            ]
        ),
    ]
}
