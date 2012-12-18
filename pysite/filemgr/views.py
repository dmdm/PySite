# -*- coding: utf-8 -*-

from pyramid.view import view_config, view_defaults
from pyramid.response import Response
import os
import logging

import pym_elfinder
from pym_elfinder.exceptions import FinderError
import pym_elfinder.cache
import pysite.sitemgr.models
import pysite.sass as sass


L = logging.getLogger('PySite')


@view_defaults(
    context=pysite.sitemgr.models.Site,
    permission='manage_files'
)
class FileMgrView(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

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
        opts = {
            'debug': False,
            'roots': [
                dict(
                    id="1",
                    driver='pym_elfinder.volume.localfilesystem',
                    path=self.context.dir_,
                    #startPath='../files/test/',
                    #URL=dirname($_SERVER['PHP_SELF']) . '/../files/',
                    # treeDeep=3,
                    # alias='File system',
                    #mimeDetect='internal',
                    #tmbPath='.tmb',
                    utf8fix=True,
                    #tmbCrop=False,
                    #tmbBgColor='transparent',
                    accessControl='access',
                    acceptedName='/^[^\.].*$/',
                    max_size=self.context.master_rc.get('max_size',
                        self.request.registry.settings['quota.max_size']),
                    # tmbSize=128,
                    attributes=[
                        dict(
                            pattern='/^[.].*$/',
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
        cache = pym_elfinder.cache.Cache(self.request.session)
        finder = pym_elfinder.Finder(opts, cache=cache,
            session=self.request.session)
        # TODO Respond with exceptions only for admin users!
        finder.respond_exceptions = True
        finder.mount_volumes()
        # TODO set user agent
        # finder.user_agent = ...
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
        sassc_url = self.request.resource_url(self.context, '@@xhr_sassc')
        return dict(sassc_url=sassc_url)

    @view_config(
        name='xhr_sassc',
        renderer='json',
    )
    def xhr_sassc(self):
        # Context is Site
        resp = pysite.lib.StatusResp()
        inf = self.context.rc.get('sass.infile', None)
        if not inf:
            resp.error('sass.infile is undefined.')
        outf = self.context.rc.get('sass.outfile', None)
        if not outf:
            resp.error('sass.outfile is undefined.')
        if not resp.is_ok:
            return resp.resp
        infile = os.path.join(self.context.dir_, os.path.normpath(
            inf.lstrip("/")))
        if not os.path.exists(infile):
            resp.error("sass.infile '{0}' does not exist".format(infile))
        if not resp.is_ok:
            return resp.resp
        is_ok, result = sass.compile_path(infile)
        if not is_ok:
            resp.add_msg(dict(kind="fatal", title="Sass compilation failed",
                text=result))
            return resp.resp
        outfile = os.path.join(self.context.dir_, os.path.normpath(
            outf.lstrip("/")))
        # Just a safeguard that we stay inside our site_dir
        if not outfile.startswith(self.context.dir_):
            resp.error("sass.outfile is invalid")
            return resp.resp
        with open(outfile, 'w', encoding='utf-8') as fh:
            fh.write(result)
        resp.ok('Sass compilation succeeded')
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
