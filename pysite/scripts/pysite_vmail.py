# -*- coding: utf-8 -*-


import transaction
import argparse
from pprint import pprint
import datetime
import sys

import pysite.lib
import pysite.cli
import pysite.usrmgr.const
import pysite.vmailmgr.manager as vmailmanager


class PySiteVmailCli(pysite.cli.Cli):

    def __init__(self):
        super().__init__()


    def list_domains(self):
        from pysite.vmailmgr.models import Domain
        qry = self._build_query(Domain)
        data = self._db_data_to_list(qry,
            fkmaps=dict(roles=lambda it: it.name))
        self._print(data)

    def add_domain(self):
        data = self._parse(self._args.data)
        data['owner'] = pysite.usrmgr.const.ROOT_UID
        rs = vmailmanager.add_domain(data)
        self._print(self._db_data_to_list([rs],
            fkmaps=dict(role_names=lambda it: it))[0])

    def update_domain(self):
        data = self._parse(self._args.data)
        data['editor'] = pysite.usrmgr.const.ROOT_UID
        data['mtime'] = datetime.datetime.now()
        rs = vmailmanager.update_domain(data)
        self._print(self._db_data_to_list([rs])[0])

    def delete_domain(self):
        rs = vmailmanager.delete_domain(self._args.id)



def main(argv=sys.argv):
    cli = PySiteVmailCli()

    # Main parser
    parser = argparse.ArgumentParser(description="""PySite-VMail command-line
        interface.""",
        epilog="""
        Samples:

        pysite-vmail -c production.ini --format tsv list-domains --order
        'domain' > /tmp/a.txt && gnumeric /tmp/a.txt
        """)
    parser.add_argument('-l', '--locale', help="""Set the desired locale.
        If omitted and output goes directly to console, we automatically use
        the console's locale.""")
    parser.add_argument('-c', '--config', required=True,
        help="""Path to INI file with configuration,
            e.g. 'production.ini'""")
    parser.add_argument('-f', '--format', default='yaml',
        choices=['yaml', 'json', 'tsv'],
        help="Set format for input and output")
    parser.add_argument('--dry-run', action="store_true",
        help="The database changes will be rolled back.")
    subparsers = parser.add_subparsers(title="Commands", dest="subparser_name",
        help="""Type 'pysite COMMAND --help'""")

    # Parent parser for DB editing
    parser_db_edit = argparse.ArgumentParser(description="Database editing",
        add_help=False)
    parser_db_edit.add_argument('data',
        help="The data. For updates, field ID must be present.")

    # Parent parser for DB deleting
    parser_db_delete = argparse.ArgumentParser(description="Database deleting",
        add_help=False)
    parser_db_delete.add_argument('id', type=int,
        help="The ID")

    # Parent parser for DB listers
    parser_db_lister = argparse.ArgumentParser(description="Database lister",
        add_help=False)
    parser_db_lister.add_argument('idlist', nargs='*', type=int, metavar='ID',
        help="""Filter by these IDs""")
    parser_db_lister.add_argument('--filter',
        help="""Define filter with literal SQL (WHERE clause, e.g. 'id between
        200 and 300')""")
    parser_db_lister.add_argument('--order',
        help="""Define sort order with literal SQL (ORDER BY clause, e.g. 'name
        DESC')""")

    # Parser cmd list-domains
    parser_list_domains = subparsers.add_parser('list-domains',
        parents=[parser_db_lister],
        help="List domains")
    parser_list_domains.set_defaults(func=cli.list_domains)

    # Parser cmd add-domain
    parser_add_domain = subparsers.add_parser('add-domain',
        parents=[parser_db_edit],
        help="Add domain",
        epilog="""You might want to try command 'list-domains'
            to see which fields are available."""
    )
    parser_add_domain.set_defaults(func=cli.add_domain)

    # Parser cmd update-domain
    parser_update_domain = subparsers.add_parser('update-domain',
        parents=[parser_db_edit],
        help="Update domain with given ID",
        epilog="""You might want to try command 'list-domains'
            to see which fields are available."""
    )
    parser_update_domain.set_defaults(func=cli.update_domain)

    # Parser cmd delete-domain
    parser_delete_domain = subparsers.add_parser('delete-domain',
        parents=[parser_db_delete],
        help="Delete domain with given ID",
    )
    parser_delete_domain.set_defaults(func=cli.delete_domain)


    # Parse args and run command
    args = parser.parse_args()
    ###pprint(args); sys.exit()
    pysite.lib.init_cli_locale(args.locale, print_info=True)
    cli.init_app(args)
    transaction.begin()
    try:
        args.func()
        if args.dry_run:
            transaction.abort()
        else:
            transaction.commit()
    except:
        transaction.abort()
        raise
    print("Done.", file=sys.stderr)
