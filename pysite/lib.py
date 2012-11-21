# coding: utf-8

import re
import anyjson


_RE_NAME_CHARS = re.compile('^[-a-zA-Z0-9_.]+$')


def validate_name(s):
    if _RE_NAME_CHARS.match(s) is None:
        raise KeyError("Invalid name: '{0}'".format(s))


def build_breadcrumbs(request):
    from pyramid.location import lineage
    linea = list(lineage(request.context))
    bcs = []
    for i, elem in enumerate(reversed(linea)):
        bc = [request.resource_url(elem)]
        if i == 0:
            bc.append('Home')
        else:
            bc.append(elem.title)
        bcs.append(bc)
    if request.view_name:
        bcs.append([None, request.view_name])
    return bcs


def build_growl_msgs(request):
    mq = []
    for m in request.session.pop_flash():
        if isinstance(m, dict):
            mq.append(anyjson.serialize(m))
        else:
            mq.append(anyjson.serialize(dict(kind="notice", text=m)))
    return mq
