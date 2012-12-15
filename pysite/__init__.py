# coding: utf-8

import os.path
import markdown

from   pyramid.config         import Configurator
from   pyramid_beaker         import session_factory_from_settings
from   pyramid.authentication import SessionAuthenticationPolicy
from   pyramid.authorization  import ACLAuthorizationPolicy

from   pysite.rc              import Rc
import pysite.resmgr
import pysite.security
import pysite.models
import pysite.i18n


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    # Init Rc
    # Get Rc instance like this, then use its methods e.g. g() or s():
    #     request.registry.settings['rc']
    # Rc data is merged directly into settings, so you can retrieve it like
    # this:
    #     request.registry.settings['project']
    # Set Rc's root_dir, which by default is the project dir (not the package
    # dir)
    #     ProjectDir
    #     +-- pym
    #     |   `-- rc.py
    #     `-- PackageDir
    if 'environment' not in settings:
        raise KeyError('Missing key "environment" in config. Specify '
            'environment in paster INI file.')
    rc = Rc(environment=settings['environment'],
        root_dir=os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..')
        )
    )
    rc.load()
    settings.update(rc.data)
    # Put rc into config settings
    settings['rc'] = rc

    # Create config
    config = Configurator(
        settings=settings
    )
    config.include(includeme)

    return config.make_wsgi_app()


def includeme(config):
    # Init the SITES_DIR
    pysite.sitemgr.models.Sites.SITES_DIR = config.registry.settings['sites_dir']
    # Init resource root
    config.set_root_factory(pysite.resmgr.root_factory)

    # Init session
    session_factory = session_factory_from_settings(config.registry.settings)
    config.set_session_factory(session_factory)

    # Init Auth and Authz
    auth_pol = SessionAuthenticationPolicy(
        callback=pysite.security.group_finder
    )
    authz_pol = ACLAuthorizationPolicy()
    config.set_request_property(pysite.security.get_user, 'user', reify=True)
    config.set_authentication_policy(auth_pol)
    config.set_authorization_policy(authz_pol)

    # i18n
    #config.add_translation_dirs('pysite:locale/')
    #config.add_translation_dirs('deform:locale/')
    config.set_locale_negotiator(pysite.i18n.locale_negotiator)

    # Init DB
    pysite.models.init(config.registry.settings, 'db.pysite.sa.')

    # Run scan() which also imports db models
    config.scan('pysite')

    # Static assets for this project
    config.add_static_view('static-pysite', 'pysite:static')

    # Add static views for assets directory of each site
    _add_site_assets(config)

    # Provide a markdown renderer
    _add_markdown(config)


def _init_vmail(rc):
    """
    Inits vmail component.

    Though I am declared as private, CLI scripts like tests
    are allowed (and must) call me during their initialisation.
    """
    pysite.vmailmgr.manager.UID = rc.g('vmail.uid',
        pysite.vmailmgr.manager.UID)
    pysite.vmailmgr.manager.GID = rc.g('vmail.gid',
        pysite.vmailmgr.manager.GID)
    pysite.vmailmgr.manager.MAX_MAILBOXES = rc.g('vmail.max_mailboxes',
        pysite.vmailmgr.manager.MAX_MAILBOXES)
    pysite.vmailmgr.manager.MAX_ALIASES = rc.g('vmail.max_aliases',
        pysite.vmailmgr.manager.MAX_ALIASES)
    pysite.vmailmgr.manager.QUOTA = rc.g('vmail.quota',
        pysite.vmailmgr.manager.QUOTA)
    pysite.vmailmgr.manager.ROOT_DIR = rc.g('vmail.root_dir',
        pysite.vmailmgr.manager.ROOT_DIR)
    pysite.vmailmgr.manager.HOME_DIR = rc.g('vmail.home_dir',
        pysite.vmailmgr.manager.HOME_DIR)
    pysite.vmailmgr.manager.MAIL_DIR = rc.g('vmail.mail_dir',
        pysite.vmailmgr.manager.MAIL_DIR)


def _add_markdown(config):
    """
    Creates application-wide instance of Markdown.

    Instance of Markdown is stored in the registry, so we create it
    once and can use it in each request: ``request.registry.pysite_markdown``.
    """
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
    # Instanciate Markdown once per application and re-use it in each
    # request
    config.registry.pysite_markdown = markdown.Markdown(**opts)


def _add_site_assets(config):
    """
    Creates static route to the assets directory of each site.

    The route name is ``stattic-`` appended with the site's name, e.g.
    ``static-www.sample.com``.
    """
    sites_dir = config.registry.settings['sites_dir']
    for f in os.listdir(sites_dir):
        ff = os.path.join(sites_dir, f)
        if os.path.isdir(ff):
            config.add_static_view('static-' + f, os.path.join(ff, 'assets'))
