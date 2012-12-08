# -*- coding: utf-8 -*-

"""
``pysite`` has several subcommands to manage your PySite setup: you can
manage principals (users), roles and role memberships as well as install new
sites and check the integrity of existing sites.

The subcommands are::

    list-principals     List principals
    add-principal       Add principal
    update-principal    Update principal with given ID
    delete-principal    Delete principal with given ID
    list-roles          List roles
    add-role            Add role
    update-role         Update role with given ID
    delete-role         Delete role with given ID
    list-rolemembers    List rolemembers
    add-rolemember      Add rolemember
    delete-rolemember   Delete rolemember with given ID
    list-sites          List sites
    add-site            Add site

Type ``pysite -h`` for general help and a list of the subcommands,
``pysite subcommand -h`` to get help for that subcommand.

``pysite`` allows you to use different formats for input and output.
Choices are json, yaml (default) and tsv.

Tsv is handy if you want to review the output in a spreadsheet::

    pysite -c production.ini --format tsv list-principals > a && gnumeric a

Both, json and yaml allow inline-style. Here is an example of inline YAML::

    pysite -c production.ini --format yaml add-principal \\
        '{principal: FOO5, email: foo5@here, pwd: FOO, roles: [foo, bar]}'
    TTY? True
    Locale? en_GB UTF-8
    id: 106
    display_name: FOO5
    email: foo5@here
    first_name: null
    gui_token: null
    identity_url: null
    is_blocked: false
    is_enabled: false
    last_name: null
    login_time: null
    notes: null
    prev_login_time: null
    principal: FOO5
    pwd: FOO
    owner: 2
    ctime: '2012-12-07 07:47:23'
    editor: null
    mtime: null
    role_names:
    - foo
    - bar
    - users
    Done.

Here is an example of creating a new site::

    pysite -c production.ini --format yaml add-site '{sitename: www.new-site.com, principal: {principal: sally, email: sally@example.com, pwd: FOO, first_name: Sally, last_name: Müller-Lüdenscheidt, roles: [some_role, other_role]}, title: Neue Site, site_template: default}'
    TTY? True
    Locale? en_GB UTF-8
    Proceed to create a site in /tmp/sites (yes/NO)? yes
    Copied template [...]/var/site-templates/default
    Added role 'www.new-site.com' (108)
    Added principal 'sally' (111)
    Set principal 'sally' as member of role 'www.new-site.com'
    Done.

To get an overview, which user is in which role, and if there are orphans (should not),
do::

    pysite -c production.ini --format tsv list-rolemembers > a && gnumeric a

"""

import os
import sys
import transaction
import argparse
import yaml
from pprint import pprint
from collections import OrderedDict
import json
import datetime

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

import pysite.models
import pysite.lib
from pysite.rc import Rc
import pysite.usrmgr.manager as usrmanager
import pysite.sitemgr.manager as sitemanager


# Init YAML to dump an OrderedDict like a regular dict, i.e.
# without creating a specific object tag.
def _represent_ordereddict(self, data):
    return self.represent_mapping('tag:yaml.org,2002:map', data.items())

yaml.add_representer(OrderedDict, _represent_ordereddict)


class PySiteCli(object):

    def __init__(self):
        self.dump_opts_json = dict(
            sort_keys=False,
            indent=4,
            ensure_ascii=False
        )
        self.dump_opts_yaml = dict(
            allow_unicode=True,
            default_flow_style=False
        )

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
                os.path.join(os.path.dirname(__file__), '..', '..')
            )
        )
        rc.load()
        settings.update(rc.data)
        settings['rc'] = rc

        pysite.models.init(settings, 'db.pysite.sa.')

        self._rc = rc
        self._settings = settings

    def _db_data_to_list(self, rs, fkmaps=None):
        """
        Transmogrifies db data into list including relationships.

        We use :func:`~.pysite.models.todict` to turn an entity into a dict, which
        will only catch regular field, not foreign keys (relationships).
        Parameter ``fkmaps`` is a dict that maps relationship names to functions.
        The function must have one input parameter which obtains a reference to
        the processed foreign entity. The function then returns the computed value.

        E.g.::

            class Principal(DbBase):
                roles = relationship(Role)

        If accessed, member ``roles`` is a list of associated roles. For each role
        the mapped function is called and the current role given::

            for attr, func in fkmaps.items():
                r[attr] = [func(it) for it in getattr(obj, attr)]

        And the function is defined like this::
            
            fkmaps=dict(roles=lambda it: it.name)

        :param rs: Db resultset, like a list of entities
        :param fkmaps: Dict with foreign key mappings
        """
        rr = []
        for obj in rs:
            it = pysite.models.todict(obj)
            r = OrderedDict()
            r['id'] = it['id']
            for k in sorted(it.keys()):
                if k in ['id', 'owner', 'ctime', 'editor', 'mtime']:
                    continue
                r[k] = it[k]
            for k in ['owner', 'ctime', 'editor', 'mtime']:
                try:
                    r[k] = it[k]
                except KeyError:
                    pass
            if fkmaps:
                for attr, func in fkmaps.items():
                    r[attr] = [func(it) for it in getattr(obj, attr)]
            rr.append(r)
        return rr

    def _print(self, data):
        fmt = self._args.format.lower()
        if fmt == 'json':
            self._print_json(data)
        elif fmt == 'tsv':
            self._print_tsv(data)
        else:
            self._print_yaml(data)

    def _print_json(self, data):
        print(json.dumps(data, **self.dump_opts_json))

    def _print_tsv(self, data):
        try:
            hh = data[0].keys()
            print("\t".join(hh))
        except KeyError:  # missing data[0]
            # Data was not a list, maybe a dict
            hh = data.keys()
            print("\t".join(hh))
            print("\t".join([str(v) for v in data.values()]))
        except AttributeError:  # missing data.keys()
            # Data is just a list
            print("\t".join(data))
        else:
            # Data is list of dicts (like resultset from DB)
            for row in data:
                print("\t".join([str(v) for v in row.values()]))

    def _print_yaml(self, data):
        yaml.dump(data, sys.stdout, **self.dump_opts_yaml)

    def _parse(self, data):
        fmt = self._args.format.lower()
        if fmt == 'json':
            return self._parse_json(data)
        if fmt == 'tsv':
            return self._parse_tsv(data)
        else:
            return self._parse_yaml(data)

    def _parse_json(self, data):
        return json.loads(data)

    def _parse_tsv(self, data):
        data = []
        for row in "\n".split(data):
            data.append([x.strip() for x in "\t".split(row)])
        return data

    def _parse_yaml(self, data):
        return yaml.load(data)

    def _build_query(self, entity):
        sess = pysite.models.DbSession()
        qry = sess.query(entity)
        if self._args.idlist:
            qry = qry.filter(entity.id.in_(self._args.idlist))
        else:
            if self._args.filter:
                qry = qry.filter(self._args.filter)
        if self._args.order:
            qry = qry.order_by(self._args.order)
        return qry

    def list_principals(self):
        from pysite.usrmgr.models import Principal
        qry = self._build_query(Principal)
        data = self._db_data_to_list(qry,
            fkmaps=dict(roles=lambda it: it.name))
        self._print(data)

    def add_principal(self):
        data = self._parse(self._args.data)
        data['owner'] = pysite.usrmgr.const.ROOT_UID
        rs = usrmanager.add_principal(data)
        self._print(self._db_data_to_list([rs],
            fkmaps=dict(role_names=lambda it: it))[0])

    def update_principal(self):
        data = self._parse(self._args.data)
        data['editor'] = pysite.usrmgr.const.ROOT_UID
        data['mtime'] = datetime.datetime.now()
        rs = usrmanager.update_principal(data)
        self._print(self._db_data_to_list([rs])[0])

    def delete_principal(self):
        rs = usrmanager.delete_principal(self._args.id)

    def list_roles(self):
        from pysite.usrmgr.models import Role
        qry = self._build_query(Role)
        data = self._db_data_to_list(qry)
        self._print(data)

    def add_role(self):
        data = self._parse(self._args.data)
        data['owner'] = pysite.usrmgr.const.ROOT_UID
        rs = usrmanager.add_role(data)
        self._print(self._db_data_to_list([rs])[0])

    def update_role(self):
        data = self._parse(self._args.data)
        data['editor'] = pysite.usrmgr.const.ROOT_UID
        data['mtime'] = datetime.datetime.now()
        rs = usrmanager.update_role(data)
        self._print(self._db_data_to_list([rs])[0])

    def delete_role(self):
        rs = usrmanager.delete_role(self._args.id)

    def list_rolemembers(self):
        from pysite.usrmgr.models import Principal, Role, RoleMember
        # Outer join to make orphans visible
        qry = self._build_query(RoleMember) \
            .outerjoin(Role) \
            .outerjoin(Principal, RoleMember.principal_id == Principal.id) \
            .add_columns(
                RoleMember.id,
                Role.id,
                Role.name,
                Principal.id,
                Principal.principal,
                Principal.is_enabled,
                Principal.is_blocked,
                RoleMember.owner,
                RoleMember.ctime
            )
        fields = ['id', 'role_id', 'role', 'principal_id', 'principal',
            'is_enabled', 'is_blocked', 'owner', 'ctime']
        data = []
        for row in qry.all():
            data.append(OrderedDict(zip(fields, row[1:])))
        self._print(data)

    def add_rolemember(self):
        data = self._parse(self._args.data)
        data['owner'] = pysite.usrmgr.const.ROOT_UID
        rs = usrmanager.add_rolemember(data)
        self._print(self._db_data_to_list([rs])[0])

    def delete_rolemember(self):
        rs = usrmanager.delete_rolemember(self._args.id)

    def list_sites(self):
        from pysite.ansi import color, error, warn, bright
        from glob import glob
        sites_dir = self._rc.g('sites_dir')
        print("Sites dir:", bright(sites_dir))
        dirs = [it for it in glob(os.path.join(sites_dir, '*'))
            if os.path.isdir(it)]
        yamls = glob(os.path.join(sites_dir, '*.yaml'))
        err = []
        for y in yamls:
            if y[:-5] not in dirs:
                err.append(y)
        if err:
            print(error("YAML files with missing site dir:"))
            for e in err:
                print("-", e)
        for sitename in dirs:
            info = sitemgr.check_site(sites_dir, sitename)
            print("\nSite " + bright(sitename) + ":")
            if info['rc'] is not None:
                print("Settings:")
                self._print(info['rc'])
            if info['manager']['rolename'] is not None:
                print("Manager: " + bright(info['manager']['rolename']))
            if info['manager']['principals'] is not None:
                self._print(info['manager']['principals'])
            for w in info['warnings']:
                print(warn(w))
            for e in info['errors']:
                print(error(e))

    def add_site(self):
        from pysite.ansi import color, error, warn, bright
        from glob import glob
        if self._args.data == 'help':
            print(sitemgr.add_site.__doc__)
            return
        data = self._parse(self._args.data)
        sites_dir = self._rc.g('sites_dir')
        inp = input("Proceed to create a site in {0} (yes/NO)? ".format(
            bright(sites_dir)))
        if inp != "yes":
            print(warn("Aborted"))
            return
        info = sitemanager.add_site(pysite.usrmgr.const.ROOT_UID, sites_dir, data)
        for m in info['msgs']:
            print(m)
        for w in info['warnings']:
            print(warn(w))
        for e in info['errors']:
            print(error(e))
        if len(info['errors']):
            raise Exception("Errors occurred. Rolling back database. "
                + bright("Created files you must remove manually."))

    def delete_site(self):
        print("""
        To delete a site, many factors have to be considered. Do you want to
        delete the files or keep them? Maybe you have more than one role
        configured in the site's ACL. Do you want to delete them all or keep
        some? Maybe some of these roles are used by other sites and must
        therefore be left untouched. Do you want to delete the principals which
        are members of those roles? As with roles, maybe some proncipals are
        used elsewehere.

        The resulting situation is too difficult to handle for such a simple
        script like me. Please perform the necessary steps to delete a site
        manually.

        To summarise:

        - Delete the files
        - Delete principals (``pysite delete-principal``)
        - Delete roles (``pysite delete-role``)
        """)


def main(argv=sys.argv):
    cli = PySiteCli()

    # Main parser
    parser = argparse.ArgumentParser(description="""PySite command-line
        interface.""",
        epilog="""
        Samples:

        pysite -c production.ini --format tsv list-rolemembers --order
        'role_name, principal_principal' > /tmp/a.txt && gnumeric /tmp/a.txt
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

    # Parser cmd list-principals
    parser_list_principals = subparsers.add_parser('list-principals',
        parents=[parser_db_lister],
        help="List principals")
    parser_list_principals.set_defaults(func=cli.list_principals)

    # Parser cmd add-principal
    parser_add_principal = subparsers.add_parser('add-principal',
        parents=[parser_db_edit],
        help="Add principal",
        epilog="""You might want to try command 'list-principals'
            to see which fields are available."""
    )
    parser_add_principal.set_defaults(func=cli.add_principal)

    # Parser cmd update-principal
    parser_update_principal = subparsers.add_parser('update-principal',
        parents=[parser_db_edit],
        help="Update principal with given ID",
        epilog="""You might want to try command 'list-principals'
            to see which fields are available."""
    )
    parser_update_principal.set_defaults(func=cli.update_principal)

    # Parser cmd delete-principal
    parser_delete_principal = subparsers.add_parser('delete-principal',
        parents=[parser_db_delete],
        help="Delete principal with given ID",
    )
    parser_delete_principal.set_defaults(func=cli.delete_principal)

    # Parser cmd list-roles
    parser_list_roles = subparsers.add_parser('list-roles',
        parents=[parser_db_lister],
        help="List roles")
    parser_list_roles.set_defaults(func=cli.list_roles)

    # Parser cmd add-role
    parser_add_role = subparsers.add_parser('add-role',
        parents=[parser_db_edit],
        help="Add role")
    parser_add_role.set_defaults(func=cli.add_role)

    # Parser cmd update-role
    parser_update_role = subparsers.add_parser('update-role',
        parents=[parser_db_edit],
        help="Update role with given ID")
    parser_update_role.set_defaults(func=cli.update_role)

    # Parser cmd delete-role
    parser_delete_role = subparsers.add_parser('delete-role',
        parents=[parser_db_delete],
        help="Delete role with given ID")
    parser_delete_role.set_defaults(func=cli.delete_role)

    # Parser cmd list-rolemembers
    parser_list_rolemembers = subparsers.add_parser('list-rolemembers',
        parents=[parser_db_lister],
        help="List rolemembers")
    parser_list_rolemembers.set_defaults(func=cli.list_rolemembers)

    # Parser cmd add-rolemember
    parser_add_rolemember = subparsers.add_parser('add-rolemember',
        parents=[parser_db_edit],
        help="Add rolemember")
    parser_add_rolemember.set_defaults(func=cli.add_rolemember)

    # Parser cmd delete-rolemember
    parser_delete_rolemember = subparsers.add_parser('delete-rolemember',
        parents=[parser_db_delete],
        help="Delete rolemember with given ID")
    parser_delete_rolemember.set_defaults(func=cli.delete_rolemember)

    # Parser cmd list-sites
    parser_list_sites = subparsers.add_parser('list-sites',
        help="List sites")
    parser_list_sites.set_defaults(func=cli.list_sites)

    # Parser cmd add-site
    parser_add_site = subparsers.add_parser('add-site',
        parents=[parser_db_edit],
        help="Add site", epilog="""Use "help" as data to obtain help about
        the data structure.""")
    parser_add_site.set_defaults(func=cli.add_site)

    # Parser cmd delete-site
    parser_delete_site = subparsers.add_parser('delete-site',
        help="Delete site")
    parser_delete_site.set_defaults(func=cli.delete_site)

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
