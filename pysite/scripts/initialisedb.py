import os
import sys
import transaction
import argparse

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from alembic.config import Config
from alembic import command

import pysite.models
import pysite.cli
from pysite.rc import Rc
import pysite.authmgr.manager as usrmgr
from pysite.authmgr.const import *


class InitialiseDbCli(pysite.cli.Cli):

    def __init__(self):
        super().__init__()

    def run(self, args):
        pysite.models.create_all()
        alembic_cfg = Config(args.alembic_config)
        command.stamp(alembic_cfg, "head")

        with transaction.manager:
            self._setup_users()

    def _setup_users(self):
        sess = pysite.models.DbSession()
        # 1// Create principal system
        p_system = usrmgr.create_principal(dict(
            id=SYSTEM_UID,
            principal='system',
            email='system@localhost',
            first_name='system',
            display_name='System',
            owner=SYSTEM_UID,
            # Roles do not exist yet. Do not auto-create them
            roles=False
        ))

        # 2// Create roles
        # This role should not have members.
        # Not-authenticated users are automatically member of 'everyone'
        usrmgr.create_role(dict(
            id=EVERYONE_RID,
            name='everyone',
            notes='Everyone (incl. unauthenticated users)',
            owner=SYSTEM_UID,
        ))
        usrmgr.create_role(dict(
            id=SYSTEM_RID,
            name='system',
            owner=SYSTEM_UID
        ))
        r_wheel = usrmgr.create_role(dict(
            id=WHEEL_RID,
            name='wheel',
            notes='Site Admins',
            owner=SYSTEM_UID
        ))
        r_users = usrmgr.create_role(dict(
            id=USERS_RID,
            name='users',
            notes='Authenticated Users',
            owner=SYSTEM_UID
        ))
        r_unit_testers = usrmgr.create_role(dict(
            id=UNIT_TESTERS_RID,
            name='unit testers',
            notes='Unit Testers',
            owner=SYSTEM_UID
        ))

        # 3// Put 'system' into its roles
        usrmgr.create_rolemember(dict(
            role_id=r_users.id,
            principal_id=p_system.id,
            owner=SYSTEM_UID
        ))
        usrmgr.create_rolemember(dict(
            role_id=r_wheel.id,
            principal_id=p_system.id,
            owner=SYSTEM_UID
        ))

        # 4// Create principals
        usrmgr.create_principal(dict(
            id=ROOT_UID,
            principal='root',
            email='root@localhost',
            first_name='root',
            display_name='Root',
            pwd=self._rc.g('auth.user_root.pwd'),
            is_enabled=True,
            owner=SYSTEM_UID,
            roles=[r_wheel.name, r_users.name]
        ))
        usrmgr.create_principal(dict(
            id=NOBODY_UID,
            principal='nobody',
            email='nobody@localhost',
            first_name='Nobody',
            display_name='Nobody',
            is_enabled=False,
            owner=SYSTEM_UID,
            # This principal is not member of any role
            # Not-authenticated users are automatically 'nobody'
            roles=False
        ))
        usrmgr.create_principal(dict(
            id=SAMPLE_DATA_UID,
            principal='sample_data',
            email='sample_data@localhost',
            first_name='Sample Data',
            display_name='Sample Data',
            is_enabled=False,
            owner=SYSTEM_UID,
            # This principal is not member of any role
            roles=False
        ))
        usrmgr.create_principal(dict(
            id=UNIT_TESTER_UID,
            principal='unit_tester',
            email='unit_tester@localhost',
            first_name='Unit-Tester',
            display_name='Unit-Tester',
            is_enabled=False,
            owner=SYSTEM_UID,
            roles=[r_unit_testers.name]
        ))
        
        # 5// Set sequence counter for user-created things
        # XXX PostgreSQL only
        # Regular users have ID > 100
        sess.execute('ALTER SEQUENCE principal_id_seq RESTART WITH 101')
        # Regular roles have ID > 100
        sess.execute('ALTER SEQUENCE role_id_seq RESTART WITH 101')
        sess.flush()


def main(argv=sys.argv):
    cli = InitialiseDbCli()

    # Main parser
    parser = argparse.ArgumentParser(description="""InitialiseDb command-line
        interface.""",
    )
    parser.add_argument('-c', '--config', required=True,
        help="""Path to INI file with configuration,
            e.g. 'production.ini'""")
    parser.add_argument('-l', '--locale', help="""Set the desired locale.
        If omitted and output goes directly to console, we automatically use
        the console's locale.""")
    parser.add_argument('--alembic-config', required=True,
        help="Path to alembic's INI file")

    # Parse args and run command
    args = parser.parse_args()
    pysite.lib.init_cli_locale(args.locale, print_info=True)
    cli.init_app(args)
    cli.run(args)
    print("Done.", file=sys.stderr)

    print("\nDirectory 'install/db' may contain SQL scripts"
        " you have to run manually.")
