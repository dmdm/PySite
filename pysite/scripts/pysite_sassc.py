# -*- coding: utf-8 -*-


import transaction
import argparse
from pprint import pprint
import datetime
import sys
import os

import pysite.lib
import pysite.cli
import pysite.authmgr.const
import pysite.vmailmgr.manager as vmailmanager
from pysite.exc import PySiteError


class PySiteSasscCli(pysite.cli.Cli):

    def __init__(self):
        super().__init__()


    def compile(self, site):
        site_dir = os.path.join(self._rc.g('sites_dir'), site)
        rc = pysite.lib.load_site_config(site_dir, 'rc.yaml')
        resp = pysite.lib.compile_sass(site_dir, rc)
        resp.print()


def main(argv=sys.argv):
    cli = PySiteSasscCli()

    # Main parser
    parser = argparse.ArgumentParser(description="""PySite-Sassc command-line
        interface.""",
        epilog="""
        Samples:

        pysite-sassc -c production.ini www.default.local
        """)
    parser.add_argument('-c', '--config', required=True,
        help="""Path to INI file with configuration,
            e.g. 'production.ini'""")
    parser.add_argument('-l', '--locale', help="""Set the desired locale.
        If omitted and output goes directly to console, we automatically use
        the console's locale.""")
    parser.add_argument('site',
        help="Name of a site, e.g. 'www.default.local'")


    # Parse args and run command
    args = parser.parse_args()
    ###pprint(args); sys.exit()
    pysite.lib.init_cli_locale(args.locale, print_info=True)
    cli.init_app(args)
    cli.compile(args.site)
    print("Done.", file=sys.stderr)
