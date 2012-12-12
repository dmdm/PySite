# -*- coding: utf-8 -*-

import os

from pysite.exc import PySiteError
from pysite.models import DbSession
from pysite.usrmgr.models import (Principal)
from pysite.vmailmgr.models import (Domain, Mailbox, Alias)

MAX_MAILBOXES = 5
MAX_ALIASES = 5
QUOTA = 10
UID = 700
GID = 8
ROOT_DIR = '/var/vmail'
HOME_DIR = '{domain}/{user}'
MAIL_DIR = '{domain}/{user}'


def add_domain(data):
    """
    Adds a new domain record.

    Field ``tenant`` can be ID (int), principal (str) or
    an instance of a Principal.

    Data fields:
    - ``owner``: Required
    - ``tenant``: Principal

    :param data: Dict with data fields
    :returns: Instance of created domain
    """
    sess = DbSession()
    if not isinstance(data['tenant'], Principal):
        tenant = Principal.find_one(data['tenant'])
    if not 'max_mailboxes' in data:
        data['max_mailboxes'] = MAX_MAILBOXES
    if not 'max_aliases' in data:
        data['max_aliases'] = MAX_ALIASES
    if not 'quota' in data:
        data['quota'] = QUOTA
    dom = Domain()
    for k, v in data.items():
        if k == 'tenant':
            continue
        setattr(dom, k, v)
    dom.tenant = tenant
    sess.add(dom)
    sess.flush() # to get ID of domain
    return dom

def update_domain(data):
    """
    Updates a domain.

    Field ``tenant``, if given, can be ID (int), principal (str) or
    an instance of a Principal.

    Data fields:
    ``id``:     Required. ID of domain to update
    ``editor``: Required. ID of Principal
    ``mtime``:  Required

    :param data: Dict with data fields
    :returns: Instance of updated domain
    """
    sess = DbSession()
    dom = sess.query(Domain).filter(Domain.id==data['id']).one()
    for k, v in data.items():
        if k == 'tenant':
            if not isinstance(data['tenant'], Principal):
                v = Principal.find_one(data['tenant'])
        setattr(dom, k, v)
    sess.flush()
    return dom

def delete_domain(id_or_name):
    """
    Deletes a domain.

    :param id: ID of domain to delete
    """
    sess = DbSession()
    dom = Domain.find_one(id_or_name)
    print("****", dom)
    sess.delete(dom)
    sess.flush()


def add_mailbox(data):
    """
    Adds a new mailbox record.

    Field ``domain`` can be ID (int), name (str) or
    an instance of a Domain.

    Data fields:
    - ``name``: Required
    - ``owner``: Required
    - ``domain``: Domain

    :param data: Dict with data fields
    :returns: Instance of created mailbox
    """
    sess = DbSession()
    if not isinstance(data['domain'], Domain):
        dom = Domain.find_one(data['domain'])
    if len(dom.mailboxes) >= dom.max_mailboxes:
        raise PySiteError("Maximum number of mailboxes reached.")
    if not 'uid' in data:
        data['uid'] = UID
    if not 'gid' in data:
        data['gid'] = GID
    if not 'quota' in data:
        data['quota'] = dom.quota
    if not 'homedir' in data:
        data['homedir'] = HOME_DIR.format(domain=dom.name, user=data['name'])
    if not 'abshomedir' in data:
        data['abshomedir'] = os.path.join(ROOT_DIR,
            HOME_DIR.format(domain=dom.name, user=data['name']))
    if not 'absmaildir' in data:
        data['absmaildir'] = os.path.join(ROOT_DIR,
            MAIL_DIR.format(domain=dom.name, user=data['name']))
    mb = Mailbox()
    for k, v in data.items():
        if k == 'domain':
            continue
        setattr(mb, k, v)
    mb.domain = dom
    sess.add(mb)
    sess.flush() # to get ID of mailbox
    return mb

def update_mailbox(data):
    """
    Updates a mailbox.

    Field ``domain``, if given, can be ID (int), name (str) or
    an instance of a Domain.

    Data fields:
    ``id``:     Required. ID of mailbox to update
    ``editor``: Required. ID of Principal
    ``mtime``:  Required

    :param data: Dict with data fields
    :returns: Instance of updated mailbox
    """
    sess = DbSession()
    mb = sess.query(Mailbox).filter(Mailbox.id==data['id']).one()
    for k, v in data.items():
        if k == 'domain':
            if not isinstance(data['domain'], Domain):
                v = Domain.find_one(data['domain'])
        setattr(mb, k, v)
    sess.flush()
    return mb

def delete_mailbox(id_or_name):
    """
    Deletes a mailbox.

    :param id: ID of mailbox to delete
    """
    sess = DbSession()
    mb = Mailbox.find_one(id_or_name)
    sess.delete(mb)
    sess.flush()


def add_alias(data):
    """
    Adds a new alias record.

    Field ``domain`` can be ID (int), name (str) or
    an instance of a Domain.

    Data fields:
    - ``owner``: Required
    - ``domain``: Domain

    :param data: Dict with data fields
    :returns: Instance of created alias
    """
    sess = DbSession()
    if not isinstance(data['domain'], Domain):
        dom = Domain.find_one(data['domain'])
    al = Alias()
    for k, v in data.items():
        if k == 'domain':
            continue
        setattr(al, k, v)
    al.domain = dom
    sess.add(al)
    sess.flush() # to get ID of alias
    return al

def update_alias(data):
    """
    Updates a alias.

    Field ``domain``, if given, can be ID (int), name (str) or
    an instance of a Domain.

    Data fields:
    ``id``:     Required. ID of alias to update
    ``editor``: Required. ID of Principal
    ``mtime``:  Required

    :param data: Dict with data fields
    :returns: Instance of updated alias
    """
    sess = DbSession()
    al = sess.query(Alias).filter(Alias.id==data['id']).one()
    for k, v in data.items():
        if k == 'domain':
            if not isinstance(data['domain'], Domain):
                v = Domain.find_one(data['domain'])
        setattr(al, k, v)
    sess.flush()
    return al

def delete_alias(id_or_name):
    """
    Deletes a alias.

    :param id: ID of alias to delete
    """
    sess = DbSession()
    al = Alias.find_one(id_or_name)
    sess.delete(al)
    sess.flush()
