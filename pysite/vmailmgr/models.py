# -*- coding: utf-8 -*-

import sqlalchemy as sa
#from sqlalchemy import event
from sqlalchemy.orm import (
    relationship,
    backref
)
import colander
from pyramid.security import Allow

import pysite.lib
from pysite.dd import apply_mixin
from pysite.models import DbBase, DefaultMixin, DefaultMixinDd

__all__ = ['Node', 'DomainDd', 'Domain', 'Mailbox', 'Alias']


class Node(pysite.lib.BaseNode):
    __name__ = 'vmailmgr'
    __acl__ = [
        (Allow, 'r:wheel', 'admin')
    ]

    def __init__(self, parent):
        super().__init__(parent)
        self._title = 'VMail Manager'


DomainDd = {
    # This must be the same as ``__tablename__`` in a SQLAlchemy declarative.
    '__tablename__': 'vmail_domain',
    # This must be the same as ``__schema__`` in the table args of a
    # SQLAlchemy declarative.
    '__schema__': '',
    'name': {
        'type': colander.Str(),
        'title': "Name",
        'widget': None,
        'validator': colander.Length(max=100),
        'colModel': {
            'width': 200,
            'editable': True
        }
    },
    'tenant_id': {
        'type': colander.Int(),
        'missing': colander.null,
        'title': 'TenantId',
        'widget': None,
        'colModel': {
            'width': 50,
            'editable': False
        }
    },
    # Query should map `tenant.display_name' to `tenant_display_name'
    'tenant_display_name': {
        'type': colander.String(),
        'missing': colander.null,
        'title': 'Tenant',
        'widget': None,
        'colModel': {
            'width': 100,
            'editable': False
        }
    },
    'used_mailboxes': {
        'type': colander.Int(),
        'title': "Used Mailboxes",
        'widget': None,
        'colModel': {
            'width': 50,
            'editable': False
        }
    },
    'max_mailboxes': {
        'type': colander.Int(),
        'title': "Max Mailboxes",
        'widget': None,
        'validator': colander.Range(min=-1),
        'colModel': {
            'width': 50,
            'editable': True
        }
    },
    'used_aliases': {
        'type': colander.Int(),
        'title': "Used Aliases",
        'widget': None,
        'colModel': {
            'width': 50,
            'editable': False
        }
    },
    'max_aliases': {
        'type': colander.Int(),
        'title': "Max Aliases",
        'widget': None,
        'validator': colander.Range(min=-1),
        'colModel': {
            'width': 50,
            'editable': True
        }
    },
    'quota': {
        'type': colander.Int(),
        'title': "Quota [MB]",
        'widget': None,
        'validator': colander.Range(min=0),
        'colModel': {
            'width': 70,
            'editable': True
        }
    },
    'is_enabled': {
        'type': colander.Bool(),
        'title': "Enabled?",
        'widget': None,
        'colModel': {
            'width': 50,
            'editable': True,
            'edittype': 'checkbox',
            'editoptions': {'value': "True:False"},
            'formoptions': {'elmprefix': None}
        }
    }
}
apply_mixin(DomainDd, DefaultMixinDd)


class Domain(DbBase, DefaultMixin):
    """
    Domain.
    """
    __tablename__ = "vmail_domain"
    __table_args__ = (
        sa.UniqueConstraint('name'),
    )

    FIND_ONE_FIELD = 'name'

    name = sa.Column(sa.Unicode(100), nullable=False, index=True)
    """
    Domain name, i.e. domain part of email address.
    """
    tenant_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("principal.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False
    )
    """
    ID of tenant, i.e. who owns this domain.
    """
    tenant = relationship(
        'Principal',
        primaryjoin="Domain.tenant_id==Principal.id",
        backref=backref("domains", passive_deletes=True,
            cascade="all, delete-orphan")
    )
    """
    Tenant, i.e. who owns this domain.
    """
    mailboxes = relationship('Mailbox',
        primaryjoin="Mailbox.domain_id==Domain.id",
        passive_deletes=True,
        cascade="all, delete-orphan",
        order_by='Mailbox.name',
        backref="domain"
    )
    """
    Mailboxes in this domain.
    """
    aliases = relationship('Alias',
        primaryjoin="Alias.domain_id==Domain.id",
        passive_deletes=True,
        cascade="all, delete-orphan",
        order_by='Alias.name',
        backref="domain"
    )
    """
    Aliases in this domain.
    """
    max_mailboxes = sa.Column(sa.Integer, default=10, nullable=False)
    """
    Max mailboxes in this domain. 0=No mailboxes allowed, -1=unlimited.
    """
    max_aliases = sa.Column(sa.Integer, default=10, nullable=False)
    """
    Max aliases in this domain. 0=No aliases allowed, -1=unlimited.
    """
    quota = sa.Column(sa.Integer, default=10, nullable=False)
    """
    Default quota in MB for a single mailbox in this domain. Max used space for
    domain defaults to max_mailboxes*quota.
    """
    is_enabled = sa.Column(sa.Boolean, nullable=False, default=True)
    """
    Tells whether this domain is enabled or not.
    This affects all mailboxes in this domain.
    """

    def __str__(self):
        return "<Domain({id}: {name}'>".format(
            id=self.id, name=self.name)


class Mailbox(DbBase, DefaultMixin):
    """
    Mailbox.
    """
    __tablename__ = "vmail_mailbox"
    __table_args__ = (
        sa.UniqueConstraint('domain_id', 'name'),
    )

    name = sa.Column(sa.Unicode(100), nullable=False, index=True)
    """
    Name part of user's email address.
    """
    pwd = sa.Column(sa.Unicode(80), nullable=False)
    """
    Password.
    """
    uid = sa.Column(sa.Integer, nullable=False)
    """
    Unix user ID of mail user.
    """
    gid = sa.Column(sa.Integer, nullable=False)
    """
    Unix group ID of mail user.
    """
    quota = sa.Column(sa.Integer, nullable=False)
    """
    Quota in MB.
    """
    home_dir = sa.Column(sa.Unicode(255), nullable=True)
    """
    Home directory (absolute path, needed for dovecot).
    """
    mail_dir = sa.Column(sa.Unicode(255), nullable=True)
    """
    Mail directory( absolute path, needed for dovecot).
    """
    domain_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("vmail_domain.id", onupdate="CASCADE",
            ondelete="CASCADE"),
        nullable=False
    )
    """
    ID of user's domain.
    """
    is_enabled = sa.Column(sa.Boolean, nullable=False, default=True)
    """
    Tells whether this mailbox is enabled or not.
    """

    def __str__(self):
        return "<Mailbox({id}: {name}@{domain}>".format(
            id=self.id, name=self.name, domain=self.domain.name)


class Alias(DbBase, DefaultMixin):
    """
    Alias.
    """
    __tablename__ = "vmail_alias"
    __table_args__ = (
        sa.UniqueConstraint('domain_id', 'name'),
    )

    name = sa.Column(sa.Unicode(100), nullable=False, index=True)
    """
    Name part of source email address.
    """
    domain_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("vmail_domain.id", onupdate="CASCADE",
            ondelete="CASCADE"),
        nullable=False
    )
    """
    ID of source domain.
    """
    dest = sa.Column(sa.Unicode(255), nullable=False)
    """
    Full email address of destination.
    """
    is_enabled = sa.Column(sa.Boolean, nullable=False, default=True)
    """
    Tells whether this alias is enabled or not.
    """

    def __str__(self):
        return "<Alias({id}: {name}@{domain} -> {dest}>".format(
            id=self.id, name=self.name, domain=self.domain.name,
            dest=self.dest)
