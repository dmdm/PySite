# -*- coding: utf-8 -*-

from sqlalchemy import engine_from_config
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    ForeignKey,
    event
)
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    ColumnProperty
    , class_mapper
    )
from sqlalchemy.orm.collections import InstrumentedList
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

    FIND_ONE_FIELD = None

    @declared_attr
    def owner(cls):
        """ID of user who created this record."""
        return Column(Integer,
            ForeignKey("principal.id", onupdate="CASCADE", ondelete="RESTRICT"),
            nullable=False)
    
    mtime    = Column(DateTime, onupdate=func.current_timestamp(), nullable=True)
    """Timestamp, last edit time."""
    
    @declared_attr
    def editor(cls):
        """ID of user who was last editor."""
        return Column(Integer,
            ForeignKey("principal.id", onupdate="CASCADE", ondelete="RESTRICT"),
            nullable=True, onupdate=_get_current_user)

    def dump(self):
        from pysite.models import todict
        from pprint import pprint
        pprint(todict(self))
        
    @classmethod
    def find_one(cls, criterion):
        """
        Some entities have besides the PK column another one that is unique and thus
        can identify the entity. :meth:`find_one()` allows to load such an
        entity by giving as ``criterion`` either the PK value (int) or a value
        from that unique column (e.g. a str).

        Since each model may have a different unique column, :attr:`FIND_ONE_FIELD`
        denotes the name of that column. It is None if that model has no unique
        column besides the PK.

        E.g. a role can be identified by its ID (PK column) or by its name. So,
        :meth:`find_one` loads either by ``Role.find_one(12)`` or by 
        ``Role.find_one('wheel')``.
        """
        sess = DbSession()
        if isinstance(criterion, int):
            return sess.query(cls).get(criterion)
        else:
            fil = {cls.FIND_ONE_FIELD: criterion}
            return sess.query(cls).filter_by(**fil).one()



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

### # ===[ FOR SQLITE ]=======
### @event.listens_for(DbEngine, "connect")
### def set_sqlite_pragma(dbapi_connection, connection_record):
###     """
###     This is supposed to turn foreign key constraints on for SQLite, so that
###     we can use SA's ``passive_delete=True``.
### 
###     XXX Alas, (at least from CLI scripts) we get an error:
###     ``sqlalchemy.exc.InvalidRequestError: No such event 'connect' for target 'None'``
###     """
###     cursor = dbapi_connection.cursor()
###     cursor.execute("PRAGMA foreign_keys=ON")
###     cursor.close()
### # ================================

# ===[ HELPER ]===================

def todict(o, fully_qualified=False):
    """Transmogrifies data of record object into dict.

    Inspired by http://blog.mitechie.com/2010/04/01/hacking-the-sqlalchemy-base-class/
    Converts only physical table columns. Columns created by e.g. relationship() must be
    handled otherwise.

    :param rs: Data to transmogrify
    :param fully_qualified: Whether dict keys should be fully qualified (schema
        + '.' + table + '.' + column) or not (just column name)

    :rtype: Dict or list of dicts
    """
    def convert_datetime(value):
        try:
            return value.strftime("%Y-%m-%d %H:%M:%S")
        except AttributeError: # Catch AttributeError: 'NoneType' object has no attribute 'strftime'
            return None

    d = {}
    for c in o.__table__.columns:
        if isinstance(c.type, DateTime):
            value = convert_datetime(getattr(o, c.name))
        elif isinstance(c, InstrumentedList):
            value = list(c)
        else:
            value = getattr(o, c.name)

        if fully_qualified:
            k = o.__table__.schema + '.' + o.__table__.name + '.' + c.name
        else:
            k = c.name
        d[k] = value
    return d


def todata(rs, fully_qualified=False):
    """Transmogrifies a result set into a list of dicts.
    
    If ``rs`` is a single instance, only a dict is returned. If ``rs`` is a
    list, a list of dicts is returned.

    :param rs: Data to transmogrify
    :param fully_qualified: Whether dict keys should be fully qualified (schema
        + '.' + table + '.' + column) or not (just column name)

    :rtype: Dict or list of dicts
    """
    if isinstance(rs, list):
        data = []
        for row in rs:
            data.append(todict(row, fully_qualified=fully_qualified))
        return data
    else:
        return todict(rs, fully_qualified=fully_qualified)


def attribute_names(cls, kind="all"):
    if kind == 'columnproperty':
        return [prop.key for prop in class_mapper(cls).iterate_properties
            if isinstance(prop, ColumnProperty)]
    else:
        return [prop.key for prop in class_mapper(cls).iterate_properties]
