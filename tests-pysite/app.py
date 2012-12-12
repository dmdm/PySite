# -*- coding: utf-8 -*-

import yaml
from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )
import os
import transaction
import argparse
import sys

from pysite.rc import Rc
import pysite
import pysite.models
import pysite.usrmgr.manager as usrmanager
from pysite.usrmgr.const import UNIT_TESTER_UID
import pysite.vmailmgr.manager as vmailmanager


class App(object):

    FIXT_DIR = os.path.normpath(os.path.join(
        os.path.dirname(__file__), 'fixtures'))

    FIXT_GROUPS = ['roles', 'principals', 'vmail_domains',
            'vmail_mailboxes', 'vmail_aliases']

    def __init__(self):
        super().__init__()
        self.fixtures = dict()
        self.load_fixtures()

    def init_app(self, args):
        """
        Initialises Pyramid application.

        Loads config settings. Initialises SQLAlchemy.
        """
        self._args = args
        setup_logging(self._args.config)
        settings = get_appsettings(self._args.config)

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
        settings['rc'] = rc

        pysite.models.init(settings, 'db.pysite.sa.')

        self._rc = rc
        self._settings = settings

        pysite._init_vmail(rc)

    def load_fixtures(self):
        self.fixtures = dict()
        for g in self.__class__.FIXT_GROUPS:
            fn = os.path.join(self.__class__.FIXT_DIR, g) + '.yaml'
            with open(fn, 'r', encoding='utf-8') as fh:
                self.fixtures[g] = yaml.load(fh)

    def add_fixtures(self):
        from pysite.models import DbSession
        from pprint import pprint
        sess = DbSession()
        transaction.begin()
        try:
            # Add in this sequence
            for g in self.__class__.FIXT_GROUPS:
                data = self.fixtures[g]
                print("***", g)
                for it in data:
                    it['owner'] = UNIT_TESTER_UID
                    pprint(it)
                    if g == 'roles':
                        usrmanager.add_role(it)
                    elif g == 'principals':
                        usrmanager.add_principal(it)
                    elif g == 'vmail_domains':
                        vmailmanager.add_domain(it)
                    elif g == 'vmail_mailboxes':
                        vmailmanager.add_mailbox(it)
                    elif g == 'vmail_aliases':
                        vmailmanager.add_alias(it)
                    else:
                        raise Exception("Unknown fixture group: '{0}'".format(
                            g))
            transaction.commit()
        except Exception as e:
            transaction.abort()
            raise e

    def delete_fixtures(self):
        from pysite.usrmgr.models import Principal, Role
        from pysite.vmailmgr.models import Domain, Mailbox, Alias
        sess = pysite.models.DbSession()
        transaction.begin()
        try:
            # 1. Delete principals. This should cascade to rolemembers,
            #    domains (via tenant), and domain cascades to mailbox and
            #    alias.
            # 2. Delete the roles
            for it in self.fixtures['principals']:
                ent = Principal.find_one(it['principal'])
                ent.dump()
                sess.delete(ent)
            for it in self.fixtures['roles']:
                ent = Role.find_one(it['name'])
                ent.dump()
                sess.delete(ent)
            transaction.commit()
        except Exception as e:
            transaction.abort()
            raise e

def main(argv=sys.argv):
    app = App()

    # Main parser
    parser = argparse.ArgumentParser(description="""App command-line
        interface.""")
    parser.add_argument('-l', '--locale', help="""Set the desired locale.
        If omitted and output goes directly to console, we automatically use
        the console's locale.""")
    parser.add_argument('-c', '--config', required=True,
        help="""Path to INI file with configuration,
            e.g. 'production.ini'""")
    parser.add_argument('cmd',
        choices=['add-fixtures', 'delete-fixtures'],
        help="""Command to perform'""")

    # Parse args and run command
    args = parser.parse_args()
    ###pprint(args); sys.exit()
    pysite.lib.init_cli_locale(args.locale, print_info=True)
    app.init_app(args)

    if args.cmd == 'add-fixtures':
        app.add_fixtures()
    elif args.cmd == 'delete-fixtures':
        app.delete_fixtures()
    else:
        raise Exception("Unknown command")

    print("Done.", file=sys.stderr)


if __name__ == '__main__':
    main()
