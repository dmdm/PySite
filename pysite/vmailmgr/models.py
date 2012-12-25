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
        self._title = 'VMail'
        self['domain'] = NodeDomain(self)
        self['mailbox'] = NodeMailbox(self)
        self['alias'] = NodeAlias(self)


class NodeDomain(pysite.lib.BaseNode):
    __name__ = 'domain'

    def __init__(self, parent):
        super().__init__(parent)
        self._title = 'Domains'


class NodeMailbox(pysite.lib.BaseNode):
    __name__ = 'mailbox'

    def __init__(self, parent):
        super().__init__(parent)
        self._title = 'Mailboxes'


class NodeAlias(pysite.lib.BaseNode):
    __name__ = 'alias'

    def __init__(self, parent):
        super().__init__(parent)
        self._title = 'Aliases'


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
            'editable': True
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
            'editoptions': {'value': "true:false"},
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


MailboxDd = {
    # This must be the same as ``__tablename__`` in a SQLAlchemy declarative.
    '__tablename__': 'vmail_mailbox',
    # This must be the same as ``__schema__`` in the table args of a
    # SQLAlchemy declarative.
    '__schema__': '',
    'name': {
        'type': colander.Str(),
        'title': "Name",
        'widget': None,
        'validator': colander.Length(max=100),
        'colModel': {
            'width': 150,
            'editable': True
        }
    },
    'pwd': {
        'type': colander.Str(),
        'title': "Pwd",
        'widget': None,
        'validator': colander.Length(max=80),
        'colModel': {
            'width': 50,
            'editable': True
        }
    },
    'domain_id': {
        'type': colander.Int(),
        'missing': colander.null,
        'title': 'DomainId',
        'widget': None,
        'colModel': {
            'width': 50,
            'editable': True
        }
    },
    'uid': {
        'type': colander.Int(),
        'missing': colander.null,
        'title': 'UID',
        'widget': None,
        'colModel': {
            'width': 50,
            'editable': True
        }
    },
    'gid': {
        'type': colander.Int(),
        'missing': colander.null,
        'title': 'GID',
        'widget': None,
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
    'home_dir': {
        'type': colander.Str(),
        'title': "Home Dir",
        'widget': None,
        'validator': colander.Length(max=255),
        'colModel': {
            'width': 300,
            'editable': True
        }
    },
    'mail_dir': {
        'type': colander.Str(),
        'title': "Mail Dir",
        'widget': None,
        'validator': colander.Length(max=255),
        'colModel': {
            'width': 300,
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
            'editoptions': {'value': "true:false"},
            'formoptions': {'elmprefix': None}
        }
    }
}
apply_mixin(MailboxDd, DefaultMixinDd)


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


AliasDd = {
    # This must be the same as ``__tablename__`` in a SQLAlchemy declarative.
    '__tablename__': 'vmail_alias',
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
    'dest': {
        'type': colander.Str(),
        'title': "Destination",
        'widget': None,
        'validator': colander.Length(max=255),
        'colModel': {
            'width': 200,
            'editable': True
        }
    },
    'domain_id': {
        'type': colander.Int(),
        'missing': colander.null,
        'title': 'DomainId',
        'widget': None,
        'colModel': {
            'width': 50,
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
            'editoptions': {'value': "true:false"},
            'formoptions': {'elmprefix': None}
        }
    }
}
apply_mixin(AliasDd, DefaultMixinDd)


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


# Can do this only after the metadata is bound to an engine.
# When we import this module before pysite.models.init() was called, we do not
# have initialized an engine yet.
###vw_domain_browse = sa.Table('vw_vmail_domain_browse', Domain.metadata, autoload=True)
def get_vw_domain_browse():
    return sa.Table('vw_vmail_domain_browse', Domain.metadata, autoload=True)


def get_vw_mailbox_browse():
    return sa.Table('vw_vmail_mailbox_browse', Mailbox.metadata, autoload=True)


def get_vw_alias_browse():
    return sa.Table('vw_vmail_alias_browse', Mailbox.metadata, autoload=True)
