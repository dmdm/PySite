# -*- coding: utf-8 -*-

import os

from pysite.exc import PySiteError
from pysite.models import DbSession
from pysite.authmgr.models import (Principal)
from pysite.vmailmgr.models import (Domain, Mailbox, Alias)
import pysite.security
import pysite.dd


MAX_MAILBOXES = 5
MAX_ALIASES = 5
QUOTA = 10
UID = 700
GID = 8
ROOT_DIR = '/var/vmail'
HOME_DIR = '{domain}/{user}'
MAIL_DIR = '{domain}/{user}/Maildir'
PASSWORD_SCHEME = 'ldap_plaintext'


def create_domain(data):
    """
    Creates a new domain record.

    Field ``tenant`` can be ID (int), principal (str) or
    an instance of a Principal.

    Data fields:
    - ``owner``: Required
    - ``tenant``: Principal

    :param data: Dict with data fields
    :returns: Instance of created domain
    """
    # If 'tenant' is set, it may be ID, name or instance of a principal.
    if 'tenant' in data:
        if not isinstance(data['tenant'], Principal):
            data['tenant'] = Principal.find_one(data['tenant'])
        data['tenant_id'] = data['tenant'].id
        del data['tenant']
    # Set defaults
    if not 'max_mailboxes' in data:
        data['max_mailboxes'] = MAX_MAILBOXES
    if not 'max_aliases' in data:
        data['max_aliases'] = MAX_ALIASES
    if not 'quota' in data:
        data['quota'] = QUOTA
    
    sess = DbSession()
    dom = Domain()
    for k, v in data.items():
        setattr(dom, k, v)
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
    # If 'tenant' is set, it may be ID, name or instance of a principal.
    if 'tenant' in data:
        if not isinstance(data['tenant'], Principal):
            data['tenant'] = Principal.find_one(data['tenant'])
        data['tenant_id'] = data['tenant'].id
        del data['tenant']
    sess = DbSession()
    dom = sess.query(Domain).filter(Domain.id==data['id']).one()
    for k, v in data.items():
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
    sess.delete(dom)
    sess.flush()


def create_mailbox(data):
    """
    Creates a new mailbox record.

    Field ``domain`` can be ID (int), name (str) or
    an instance of a Domain.

    Data fields:
    - ``name``: Required. Str
    - ``owner``: Required. ID of Principal.
    - ``domain``: Required. Domain.
    - ``pwd``: Required. Password.

    :param data: Dict with data fields
    :returns: Instance of created mailbox
    """
    dom = None
    # If 'domain' is set, it may be ID, name or instance of a domain.
    # Load the appropriate domain and set 'domain_id'.
    if 'domain' in data:
        if not isinstance(data['domain'], Domain):
            data['domain'] = Domain.find_one(data['domain'])
        data['domain_id'] = data['domain'].id
        dom = data['domain']
        del data['domain']
    # 'domain' was not set, so load domain by its ID from 'domain_id'
    if not dom:
        dom = Domain.find_one(data['domain_id'])
    # Check that we are in limits
    if len(dom.mailboxes) >= dom.max_mailboxes:
        raise PySiteError("Maximum number of mailboxes reached.")
    # Make sure the password is encrypted
    if not data['pwd'].startswith('{'):
        data['pwd'] = pysite.security.pwd_context.encrypt(data['pwd'],
            PASSWORD_SCHEME)
    # Set defaults
    if not 'uid' in data:
        data['uid'] = UID
    if not 'gid' in data:
        data['gid'] = GID
    if not 'quota' in data:
        data['quota'] = dom.quota  # Default from domain!
    # Make sure, 'home_dir' is absolute path 
    d = data['home_dir'] if 'home_dir' in data else HOME_DIR
    d = d.format(root=ROOT_DIR, domain=dom.name, user=data['name'])
    if not d.startswith(os.path.sep):
        d = os.path.join(ROOT_DIR, d)
    data['home_dir'] = d
    # Make sure, 'mail_dir' is absolute path 
    d = data['mail_dir'] if 'mail_dir' in data else MAIL_DIR
    d = d.format(root=ROOT_DIR, domain=dom.name, user=data['name'])
    if not d.startswith(os.path.sep):
        d = os.path.join(ROOT_DIR, d)
    data['mail_dir'] = d

    sess = DbSession()
    mb = Mailbox()
    for k, v in data.items():
        setattr(mb, k, v)
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
    # If 'domain' is set, it may be ID, name or instance of a domain.
    if 'domain' in data:
        if not isinstance(data['domain'], Domain):
            data['domain'] = Domain.find_one(data['domain'])
        data['domain_id'] = data['domain'].id
        del data['domain']
    # Make sure the password is encrypted
    if 'pwd' in data and not data['pwd'].startswith('{'):
        data['pwd'] = pysite.security.pwd_context(data['pwd'],
            PASSWORD_SCHEME)

    sess = DbSession()
    mb = sess.query(Mailbox).filter(Mailbox.id==data['id']).one()
    for k, v in data.items():
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


def create_alias(data):
    """
    Creates a new alias record.

    Field ``domain`` can be ID (int), name (str) or
    an instance of a Domain.

    Data fields:
    - ``owner``: Required
    - ``domain``: Domain

    :param data: Dict with data fields
    :returns: Instance of created alias
    """
    if 'domain' in data:
        if not isinstance(data['domain'], Domain):
            data['domain'] = Domain.find_one(data['domain'])
        data['domain_id'] = data['domain'].id
        del data['domain']
    sess = DbSession()
    al = Alias()
    for k, v in data.items():
        setattr(al, k, v)
    sess.add(al)
    sess.flush() # to get ID of alias
    return al

def update_alias(data):
    """
    Updates an existing alias.

    Field ``domain``, if given, can be ID (int), name (str) or
    an instance of a Domain.

    Data fields:
    ``id``:     Required. ID of alias to update
    ``editor``: Required. ID of Principal
    ``mtime``:  Required

    :param data: Dict with data fields
    :returns: Instance of updated alias
    """
    if 'domain' in data:
        if not isinstance(data['domain'], Domain):
            data['domain'] = Domain.find_one(data['domain'])
        data['domain_id'] = data['domain'].id
        del data['domain']
    sess = DbSession()
    al = sess.query(Alias).filter(Alias.id==data['id']).one()
    for k, v in data.items():
        setattr(al, k, v)
    sess.flush()
    return al

def delete_alias(id_or_name):
    """
    Deletes an alias.

    :param id: ID of alias to delete
    """
    sess = DbSession()
    al = Alias.find_one(id_or_name)
    sess.delete(al)
    sess.flush()
