import os
import sys
import transaction

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

import pysite.models
from pysite.rc import Rc
from pysite.authmgr.install import setup_users


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd)) 
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)

    if 'environment' not in settings:
        raise KeyError('Missing key "environment" in config. Specify '
            'environment in paster INI file.')
    rc = Rc(environment=settings['environment'],
        root_dir=os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', '..')
        )
    )
    rc.load()
    settings.update(rc.data)
    settings['rc'] = rc

    pysite.models.init(settings, 'db.pysite.sa.')
    pysite.models.create_all()
    with transaction.manager:
        setup_users(rc)
