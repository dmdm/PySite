# -*- coding: utf-8 -*-

from sqlalchemy import engine_from_config
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    ForeignKey
)
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.sql.expression import func

from zope.sqlalchemy import ZopeTransactionExtension

import pyramid.threadlocal

def _get_current_user():
    cr = pyramid.threadlocal.get_current_request()
    return cr.user.uid


# ===[ DB HELPERS ]=======

DbSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
"""Factory for DB session."""
DbBase = declarative_base()
"""Our base class for declarative models."""
DbEngine = None
"""Default DB engine."""

class DefaultMixin(object):
    """Mixin to add Parenchym's standard fields to a model class.

    These are: id, ctime, owner, mtime, editor.
    """

    id       = Column(Integer, primary_key=True, nullable=False)
    """Primary key of table."""

    ctime    = Column(DateTime, server_default=func.current_timestamp(), nullable=False)
    """Timestamp, creation time."""

    @declared_attr
    def owner(cls):
        """ID of user who created this record."""
        return Column(Integer,
            #ForeignKey("pym.principal.id", onupdate="CASCADE", ondelete="RESTRICT"),
            ForeignKey("principal.id", onupdate="CASCADE", ondelete="RESTRICT"),
            nullable=False)
    
    mtime    = Column(DateTime, onupdate=func.current_timestamp(), nullable=True)
    """Timestamp, last edit time."""
    
    @declared_attr
    def editor(cls):
        """ID of user who was last editor."""
        return Column(Integer,
            #ForeignKey("pym.principal.id", onupdate="CASCADE", ondelete="RESTRICT"),
            ForeignKey("principal.id", onupdate="CASCADE", ondelete="RESTRICT"),
            nullable=True, onupdate=_get_current_user)


# ================================



# ===[ IMPORTABLE SETUP FUNCS ]=======

def init(config, prefix):
    """Initializes SQLAlchemy by rc settings.

    Creates engine, binds session and declarative base.
    """
    global DbEngine
    DbEngine = engine_from_config(config, prefix)
    DbSession.configure(bind=DbEngine)
    DbBase.metadata.bind = DbEngine

def create_all():
    """Creates bound data model."""
    DbBase.metadata.create_all(DbEngine)

# ================================
