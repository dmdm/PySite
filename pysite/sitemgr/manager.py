# -*- coding: utf-8 -*-

import os
import yaml
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

import pysite.models
from pysite.authmgr.models import Principal, Role


def check_site(sites_dir, sitename):
    """
    Checks integrity of a site.

    A site is integer if:

    - It has a matching subdirectory in SITES_DIR
    - It has a matching YAML file in SITES_DIR
    - Its master rc at least has settings for
      - ``max_size``
    - Its master ACL has at least one entry for a file manager:
      - Permission "allow"
      - List of principals contains at least one role (i.e. the manager role)
      - Permission name is 'manage_files'
    - The manager role exists in the database
    - The manager role has at least one member

    :param site_dir: The SITE_DIR, e.g. as configured in the app's rc file
    :param sitename: Name of site to check
    :returns: Returns a dict with the collected information. Key ``rc`` has
              the loaded configuration (or None) and ``manager`` has details
              about the manager: It is a dict with keys ``rolename`` and
              ``principals``. And if errors or warnings occured, respective
              keys are set (if both of them are absent, everything went well).
    """
    errors = []
    warnings = []
    dir_ = os.path.join(sites_dir, sitename)
    info = dict(rc=None, manager=dict(rolename=None, principals=None),
        errors=errors, warnings=warnings)
    sess = pysite.models.DbSession()

    def _check_dir():
        if not os.path.exists(dir_):
            errors.append("Site directory does not exist: '{0}'".format(
                dir_))
            return False
        if not os.path.isdir(dir_):
            errors.append("Site is not a directory: '{0}'".format(
                dir_))
            return False
        return True

    def _load_rc(fn):
        with open(fn, 'r', encoding='utf-8') as fh:
            return yaml.load(fh)

    def _check_rc(rc):
        # Process all warnings without stopping
        if rc:
            if not 'max_size' in rc:
                warnings.append("Rc has 'max_size' not set. Default applies.")
            if not 'acl' in rc:
                warnings.append("Rc has no ACL.")
        else:
            warnings.append("Master rc has no settings")

    def _check_acl(acl):
        for ace in acl:
            if 'allow'.startswith(ace[0].lower()) \
                    and ace[2] == 'manage_files':
                rolename = ace[1][2:] if ace[1].startswith('r:') else ace[1]
                try:
                    role = sess.query(Role).filter(Role.name == rolename).one()
                except NoResultFound:
                    errors.append("Role '{0}' does not exist".format(rolename))
                    return False
                info['manager']['rolename'] = "{0} ({1})".format(role.name,
                    role.id)
                info['_role'] = role
                return True
        # No role was set or allowed
        warnings.append("""ACL contains no role that is permitted
            'manage_files'""")
        return True  # still return True, this is a warning, no error

    def _check_rolemember(role):
        qry = sess.query(Principal).filter(Principal.roles.any(
            name=role.name))
        principals = ["{0} ({1})".format(p.principal, p.id)
            for p in qry.all()]
        if not principals:
            errors.append("Role '{0}' has no members".format(role.name))
            return False
        info['manager']['principals'] = principals
        return True

    if not _check_dir():
        return info
    rc = _load_rc(dir_ + '.yaml')
    info['rc'] = rc
    _check_rc(rc)  # this produces only warnings
    if rc and 'acl' in rc:
        if not _check_acl(rc['acl']):
            return info
    if '_role' in info:
        if not _check_rolemember(info['_role']):
            return info
        del info['_role']

    return info


def add_site(owner, sites_dir, data):
    """
    Adds a site.

    The data must be a dict with this keys:

    - ``sitename``: Name of the site. This will be the name of the site's
      directory and its manager role.
    - ``title``: Optional. Title of the site. Will be written in the site's
      user rc.
    - ``master_rc``: Optional. Dict with settings for the master rc file.
    - ``role``: Optional. Name of the manager role. If omitted, the site's name
      is used.
    - ``principal``: Either a principal (string) of an existing principal, or a
      dict with data for a new principal.
    - ``site_template``: Optional. Specifies a site template that is copied to
      the new directory. If it starts with a path separator, e.g. `/', it is
      treated as an absolute path, else it is treated as the name of a template
      within ``var/site-templates``. If omitted, the template "default" is
      used.

    The data for a new principal must be a dict with these keys:
    ``principal``, ``email``, ``pwd``. Other keys may optionally be given, like
    ``first_name``, ``last_name``, ``display_name``, ``notes``.

    :param sites_dir: Directory where the site will be stored
    :param data: Data structure that describes the new site, see above.
    :returns: Dict with keys ``errors`` and ``warnings``.
    """
    errors = []
    warnings = []
    msgs = []
    info = dict(errors=errors, warnings=warnings, msgs=msgs)

    if 'sitename' not in data:
        errors.append("Key 'sitename' is missing from data")
        return info
    if 'principal' not in data:
        errors.append("Key 'principal' is missing from data")
        return info

    dir_ = os.path.join(sites_dir, data['sitename'])
    rolename = data['role'] if 'role' in data else data['sitename']

    site_template = data.get('site_template', 'default')
    if not site_template.startswith(os.path.sep):
        root_dir = os.path.join(os.path.dirname(__file__), '..', '..')
        site_template = os.path.join(root_dir, 'var', 'site-templates',
            site_template)

    with open(site_template + '.yaml', 'r', encoding='utf-8') as fh:
        master_rc = yaml.load(fh)
    master_rc['acl'][0][1] = 'r:' + rolename
    if 'master_rc' in data:
        master_rc.update(data['master_rc'])
    user_rc = dict(title=data['title']) if 'title' in data else None

    def _create_site_files():
        import shutil
        try:
            fn = dir_ + '.yaml'
            # Ensure the site does not exist yet
            if os.path.exists(dir_):
                raise IOError("Site directory already exists: '{0}'"
                    .format(dir_))
            if os.path.exists(fn):
                raise IOError("Master rc file already exists: '{0}'"
                    .format(fn))
            # Copy template
            if site_template:
                shutil.copytree(site_template, dir_)
                msgs.append("Copied template " + site_template)
            else:
                # Site dir
                os.mkdir(dir_)
                # Top level dirs
                dirs = ['assets', 'cache', 'plugins', 'content']
                for d in dirs:
                    os.mkdir(os.path.join(dir_, d))
            # Master rc file
            with open(fn, 'w', encoding='utf-8') as fh:
                yaml.dump(master_rc, fh, allow_unicode=True,
                        default_flow_style=False)
            # User rc file
            fn = os.path.join(dir_, 'rc.yaml')
            with open(fn, 'w', encoding='utf-8') as fh:
                if user_rc:
                    yaml.dump(user_rc, fh, allow_unicode=True,
                        default_flow_style=False)
            return True
        except IOError as e:
            errors.append(e)
            return False

    def _create_role_and_principal():
        import pysite.authmgr.manager as usrmanager
        sess = pysite.models.DbSession()
        try:
            role = sess.query(Role).filter(Role.name == rolename).one()
            msgs.append("Use existing role '{0}' ({1})".format(
                role.name, role.id))
        except NoResultFound:
            role_data = dict(
                name=rolename,
                owner=owner,
                notes="Manager role for site '{0}'".format(data['sitename'])
            )
            role = usrmanager.add_role(role_data)
            msgs.append("Added role '{0}' ({1})".format(role.name, role.id))
        if isinstance(data['principal'], dict):
            data['principal']['owner'] = owner
            principal = usrmanager.add_principal(data['principal'])
            msgs.append("Added principal '{0}' ({1})".format(
                principal.principal, principal.id))
        else:
            try:
                principal = sess.query(Principal).filter(
                    Principal.principal == data['principal']).one()
                msgs.append("Use existing principal '{0}' ({1})".format(
                    principal.principal, principal.id))
            except NoResultFound:
                errors.append("Principal '{0}' not found".format(
                    data['principal']))
                return info
        try:
            # Save these here. If add_rolemember fails, the session is
            # aborted and we cannot access the attributes of the entities
            # in the except handler.
            princ = principal.principal
            rol = role.name
            usrmanager.add_rolemember(dict(principal_id=principal.id,
                role_id=role.id, owner=owner))
            msgs.append("Set principal '{0}' as member of role '{1}'".format(
                principal.principal, role.name))
        except IntegrityError:
            msgs.append("Principal '{0}' is already member of role '{1}'".format(
                princ, rol))

    if not _create_site_files():
        return info
    try:
        _create_role_and_principal()
    except SQLAlchemyError as e:
        errors.append(e)
    return info
