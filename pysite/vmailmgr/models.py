# -*- coding: utf-8 -*-

import sqlalchemy as sa
#from sqlalchemy import event
from sqlalchemy.orm import (
    relationship,
    backref
)
from pyramid.security import Allow

import pysite.resmgr.abstractmodels
from pysite.models import DbBase, DefaultMixin

__all__ = ['Node', 'Domain', 'Mailbox', 'Alias']


class Node(pysite.resmgr.abstractmodels.Node):
    __name__ = 'VMailMgr'
    __acl__ = [
        (Allow, 'r:wheel', 'admin')
    ]

    def __init__(self, parent):
        super().__init__(parent)
        self._title = 'VMail Manager'


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
    Max mailboxes in this domain.
    """
    max_aliases = sa.Column(sa.Integer, default=10, nullable=False)
    """
    Max aliases in this domain.
    """
    quota = sa.Column(sa.Integer, default=10, nullable=False)
    """
    Default quota for a mailbox in MB. Max used space for domain defaults to
    max_mailboxes*default_quota.
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
    pwd = sa.Column(sa.Unicode(32), nullable=False)
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
    homedir = sa.Column(sa.Unicode(255), nullable=True)
    """
    Home directory (relative part below vmail.root_dir).
    """
    abshomedir = sa.Column(sa.Unicode(255), nullable=True)
    """
    Absolute path to home directory, for dovecot.
    """
    absmaildir = sa.Column(sa.Unicode(255), nullable=True)
    """
    Absolute path to mail directory, for dovecot.
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

    def __str__(self):
        return "<Alias({id}: {name}@{domain} -> {dest}>".format(
            id=self.id, name=self.name, domain=self.domain.name,
            dest=self.dest)
