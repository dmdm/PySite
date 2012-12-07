# coding: utf-8

import os.path

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
    # Init resource root
    # Also init the sites_dir
    pysite.sitemgr.models.Sites.SITES_DIR = config.registry.settings['sites_dir']
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
    add_site_assets(config)

    
def add_site_assets(config):
    sites_dir = config.registry.settings['sites_dir']
    for f in os.listdir(sites_dir):
        ff = os.path.join(sites_dir, f)
        if os.path.isdir(ff):
            config.add_static_view('static-' + f, os.path.join(ff, 'assets'))
