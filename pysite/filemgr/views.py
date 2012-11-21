# -*- coding: utf-8 -*-

from pyramid.view import view_config
from pyramid.response import Response
import os
import logging

import pym_elfinder
from pym_elfinder.exceptions import FinderError
import pym_elfinder.cache
import pysite.sitemgr.models


L = logging.getLogger('PySite')


@view_config(
    name='filemgr',
    context=pysite.sitemgr.models.Site,
    renderer='pysite:filemgr/templates/filemgr.mako',
    permission='manage_files'
)
def filemgr(context, request):
    logo_url = request.static_url('pysite:static/img/filemgr.png')
    logo_alt = 'FileManager'
    return dict(logo_url=logo_url, logo_alt=logo_alt)


@view_config(
    name='xhr_filemgr',
    context=pysite.sitemgr.models.Site,
    renderer='json',
    permission='manage_files'
)
def xhr_filemgr(context, request):
    cmd = ''
    cmd_args = dict()
    for k in request.params:
        if k == '_':
            continue
        if k == 'cmd':
            cmd = request.params[k]
        else:
            if k.endswith("[]"):
                k2 = k.rstrip("[]")
                cmd_args[k2] = request.params.getall(k)
            else:
                cmd_args[k] = request.params[k]
    opts = {
        'debug': False,
        'roots': [
            dict(
                id = "1",
                driver     = 'pym_elfinder.volume.localfilesystem',
                path = context.dir_,
                #startPath  = '../files/test/',
                #URL        = dirname($_SERVER['PHP_SELF']) . '/../files/',
                # treeDeep   = 3,
                # alias      = 'File system',
                #mimeDetect = 'internal',
                #tmbPath    = '.tmb',
                utf8fix    = True,
                #tmbCrop    = False,
                #tmbBgColor = 'transparent',
                accessControl = 'access',
                acceptedName    = '/^[^\.].*$/',
                max_size = context.master_rc.get('max_size',
                    request.registry.settings['quota.max_size']),
                # tmbSize = 128,
                attributes = [
                    dict(
                        pattern = '/^[.].*$/',
                        read = True,
                        write = False
                    ),
                    dict(
                        pattern = '/^[^.].*$/',
                        read = True,
                        write = True
                    )
                ]
            ),
        ]
    }
    cache = pym_elfinder.cache.Cache(request.session)
    finder = pym_elfinder.Finder(opts, cache=cache, session=request.session)
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
            request.response.status = e.status
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
                request.response.headers[k] = v
        return finder.response


_DEVEL_OPTS = {
    'debug': True,
    'roots': [
        dict(
            id = "1",
            driver     = 'pym_elfinder.volume.localfilesystem',
            path       = os.path.abspath(os.path.realpath(os.path.join(
                            os.path.dirname(__file__), '..', '..', '..',
                            'Pym-elFinder',
                            'pym_elfinder_tests', 'fixtures', 'files'))),
            #startPath  = '../files/test/',
            #URL        = dirname($_SERVER['PHP_SELF']) . '/../files/',
            # treeDeep   = 3,
            # alias      = 'File system',
            mimeDetect = 'internal',
            #tmbPath    = '.tmb',
            utf8fix    = True,
            #tmbCrop    = False,
            #tmbBgColor = 'transparent',
            accessControl = 'access',
            acceptedName    = '/^[^\.].*$/',
            # tmbSize = 128,
            attributes = [
                dict(
                    pattern = '/\.js$/',
                    read = True,
                    write = False
                ),
                dict(
                    pattern = '/^\/icons$/',
                    read = True,
                    write = False
                ),
                dict(
                    pattern = '/^[^.].*$/',
                    read = True,
                    write = True
                )
            ]
        ),
    ]
}
