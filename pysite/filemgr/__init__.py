# -*- coding: utf-8 -*-

import pym_elfinder
import pym_elfinder.cache


def create_finder(context, request):
    """
    Creates initialised instance of finder for given request.

    :param context: Resource of current site. NOT current page!
    :param request: Current request
    :returns: Instance of finder
    """
    opts = {
        'debug': False,
        'roots': [
            dict(
                id="1",
                driver='pym_elfinder.volume.localfilesystem',
                path=context.dir_,
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
                max_size=context.master_rc.get('max_size',
                    request.registry.settings['quota.max_size']),
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
    cache = pym_elfinder.cache.Cache(request.session)
    finder = pym_elfinder.Finder(opts, cache=cache,
        session=request.session)
    # TODO Respond with exceptions only for admin users!
    finder.respond_exceptions = True
    finder.mount_volumes()
    # TODO set user agent
    # finder.user_agent = ...
    return finder
