# -*- coding: utf-8 -*-

from sqlalchemy.orm.exc import NoResultFound
from pysite.models import DbSession
from pysite.usrmgr.models import (Principal, Role, RoleMember)


def add_principal(data):
    """
    Adds a new principal record.

    Data fields:
    - ``owner``: Required
    - ``roles``: Optional list of role names. Role 'users' is always
                 automatically set.

    :param data: Dict with data fields
    :returns: Instance of created principal
    """
    # Principal is always at least member of role "users"
    if not 'roles' in data:
        data['roles'] = []
    role_names = data['roles']
    if not 'users' in role_names:
        data['roles'].append('users')
    sess = DbSession()
    # Create principal
    p = Principal()
    for k, v in data.items():
        if k == 'roles': continue
        setattr(p, k, v)
    sess.add(p)
    sess.flush() # to get ID of principal
    # Load/create the roles and memberships
    for name in role_names:
        try:
            r = sess.query(Role).filter(Role.name==name).one()
        except NoResultFound:
            r = Role(name=name, owner=data['owner'])
            sess.add(r)
            sess.flush()
        rm = RoleMember(principal_id=p.id, role_id=r.id, owner=p.owner)
        sess.add(rm)
    sess.flush()
    return p

def update_principal(data):
    """
    Updates a principal.

    Data fields:
    ``id``:     Required. ID of principal to update
    ``editor``: Required
    ``mtime``:  Required

    :param data: Dict with data fields
    :returns: Instance of updated principal
    """
    sess = DbSession()
    p = sess.query(Principal).filter(Principal.id==data['id']).one()
    for k, v in data.items():
        setattr(p, k, v)
    sess.flush()
    return p

def delete_principal(id):
    """
    Deletes a principal.

    :param id: ID of principal to delete
    """
    sess = DbSession()
    p = sess.query(Principal).filter(Principal.id==id).one()
    sess.delete(p)
    sess.flush()


def add_role(data):
    """
    Adds a new role record.

    Data fields:
    - ``owner``: Required
    :param data: Dict with data fields
    :returns: Instance of created role
    """
    sess = DbSession()
    r = Role()
    for k, v in data.items():
        setattr(r, k, v)
    sess.add(r)
    sess.flush()
    return r

def update_role(data):
    """
    Updates a role.

    Data fields:
    ``id``:     Required. ID of role to update
    ``editor``: Required
    ``mtime``:  Required

    :param data: Dict with data fields
    :returns: Instance of updated role
    """
    sess = DbSession()
    r = sess.query(Role).filter(Role.id==data['id']).one()
    for k, v in data.items():
        setattr(r, k, v)
    sess.flush()
    return r

def delete_role(id):
    """
    Deletes a role.

    :param id: ID of role to delete
    """
    sess = DbSession()
    r = sess.query(Role).filter(Role.id==id).one()
    sess.delete(r)
    sess.flush()


def add_rolemember(data):
    """
    Adds a new rolemember record.

    Data fields:
    - ``owner``:        Required
    - ``principal_id``: Required
    - ``role_id``:      Required
    :param data: Dict with data fields
    :returns: Instance of created rolemember
    """
    sess = DbSession()
    rm = RoleMember()
    for k, v in data.items():
        setattr(rm, k, v)
    sess.add(rm)
    sess.flush()
    return rm

def delete_rolemember(id):
    """
    Deletes a rolemember.

    :param id: ID of rolemember to delete
    """
    sess = DbSession()
    rm = sess.query(RoleMember).filter(RoleMember.id==id).one()
    sess.delete(rm)
    sess.flush()

