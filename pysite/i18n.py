# -*- coding: utf-8 -*-

import pyramid.i18n

tsf = None
"""Our TranslationStringFactory.

MUST be set during application's initialisation, e.g. in ``includeme()``.
"""



def locale_negotiator(request):
    """Negotiates the locale setting.

    In config settings we have a list of available languages, key
    ``i18n.avail_languages``. First, we use Pyramid's default locale
    negotiator, and if it's value is in our available language, we use this.
    The reason is that explicitly setting the locale takes precedence.
    Set '*' as ``avail_languages`` to allow all.

    If no locale was explicitly set, we let ``request.accept_language``,
    which is a WebOb object, find the best match from our available
    languages.
    """
    avail_languages = request.registry.settings['i18n.avail_languages']
    loc = pyramid.i18n.default_locale_negotiator(request)
    if loc:
        if '*' in avail_languages or loc in avail_languages:
            return loc
    return request.accept_language.best_match(avail_languages)

