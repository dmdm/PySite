# -*- coding: utf-8 -*-

# Interesting reads:
# http://stackoverflow.com/questions/270879/efficiently-updating-database-using-sqlalchemy-orm/278606#278606
# http://stackoverflow.com/questions/9593610/creating-a-temporary-table-from-a-query-using-sqlalchemy-orm
# http://stackoverflow.com/questions/9766940/how-to-create-an-sql-view-with-sqlalchemy
# Materialized view:
# http://stackoverflow.com/questions/11114903/oracle-functional-index-creation


from sqlalchemy import (
    engine_from_config,
    Column,
    Integer,
    DateTime,
    ForeignKey,
    event
)
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    ColumnProperty,
    class_mapper
    )
import sqlalchemy.orm.query
from sqlalchemy.orm.collections import InstrumentedList
from sqlalchemy.ext.declarative import (
    declared_attr,
    declarative_base
)
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.expression import (func, Executable, ClauseElement)
import sqlalchemy.engine

from zope.sqlalchemy import ZopeTransactionExtension

import pyramid.threadlocal
import colander
import deform
import sqlparse

from pysite.exc import PySiteError


def _get_current_user():
    cr = pyramid.threadlocal.get_current_request()
    return cr.user.uid


# ===[ SCHEMA HELPERS ]=======

@colander.deferred
def deferred_csrf_default(node, kw):
    request = kw.get('request')
    csrf_token = request.session.get_csrf_token()
    return csrf_token


@colander.deferred
def deferred_csrf_validator(node, kw):
    def validate_csrf(node, value):
        request = kw.get('request')
        csrf_token = request.session.get_csrf_token()
        if value != csrf_token:
            raise ValueError('Bad CSRF token')
    return validate_csrf


CSRF_SCHEMA_NODE = colander.SchemaNode(
    colander.String(),
    default=deferred_csrf_default,
    # Don't need this. We have a subscriber checking this token
    #validator = deferred_csrf_validator,
    widget=deform.widget.HiddenWidget(),
)
"""
Colander schema node for a hidden field containing a CSRF token.

Usage::

    class LoginSchema(colander.MappingSchema):
        login = colander.SchemaNode(colander.String())
        pwd   = colander.SchemaNode(colander.String(),
                    widget=deform.widget.PasswordWidget()
                )
        csrf = CSRF_SCHEMA_NODE

When you create a schema instance, do not forget to bind the current
request like so::

    sch = LoginSchema().bind(request=self.request)
"""


class LoginSchema(colander.MappingSchema):
    """
    Schema for basic login form with CSRF token.
    """
    login = colander.SchemaNode(colander.String())
    pwd = colander.SchemaNode(colander.String(),
        widget=deform.widget.PasswordWidget()
    )
    csrf = CSRF_SCHEMA_NODE


# ===[ DB HELPERS ]=======

DbSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
"""
Factory for DB session.
"""
DbBase = declarative_base()
"""
Our base class for declarative models.
"""
DbEngine = None
"""
Default DB engine.
"""


@colander.deferred
def _deferred_validate_by_action(node, kw):
    ac = kw.get('action', None)
    if ac not in ['create', 'update']:
        raise PySiteError("Invalid action (allowed: 'create',"
            "'update'): '{0}'".format(ac))
    def validator(node, value):
        if ac == 'create':
            # ID may or may not be defined for a create.
            if node.name == 'owner':
                if value is None or value == '':
                    raise colander.Invalid(node, node.name + ' must be set')
            elif node.name == 'ctime':
                if value is None or value == '':
                    raise colander.Invalid(node, node.name + ' must be set')
            elif node.name == 'editor':
                if value is not None:
                    raise colander.Invalid(node, node.name + ' must NOT be set')
            elif node.name == 'mtime':
                if value is not None:
                    raise colander.Invalid(node, node.name + ' must NOT be set')
        else:
            if node.name == 'id':
                if value is None or value == '':
                    raise colander.Invalid(node, node.name + ' must be set')
            elif node.name == 'owner':
                if value is not None:
                    raise colander.Invalid(node, node.name + ' must NOT be set')
            elif node.name == 'ctime':
                if value is not None:
                    raise colander.Invalid(node, node.name + ' must NOT be set')
            elif node.name == 'editor':
                if value is None or value == '':
                    raise colander.Invalid(node, node.name + ' must be set')
            elif node.name == 'mtime':
                if value is None or value == '':
                    raise colander.Invalid(node, node.name + ' must be set')
    return validator


DefaultMixinDd = {
    'id': {
        'type': colander.Int(),
        # On create, ID may be missing
        # On update, ID is required
        'missing': colander.null,
        'validator': _deferred_validate_by_action,
        'title': 'Id',
        'widget': None,
        'colModel': {
            'width': 40,
            'editable': False
        }
    },
    'owner': {
        'type': colander.Int(),
        # On create, owner is required
        # On update, owner must be missing
        'missing': colander.null,
        'title': 'OwnerId',
        'widget': None,
        'colModel': {
            'width': 50,
            'editable': False
        }
    },
    'editor': {
        'type': colander.Int(),
        # On create, editor must be missing
        # On update, editor is required
        'missing': colander.null,
        'title': 'EditorId',
        'widget': None,
        'colModel': {
            'width': 50,
            'editable': False
        }
    },
    'ctime': {
        'type': colander.DateTime(default_tzinfo=None),
        # On create, ctime is required
        # On update, ctime must be missing
        'missing': colander.null,
        'title': 'Created At',
        'widget': None,
        'colModel': {
            'width': 130,
            'editable': False
        }
    },
    'mtime': {
        'type': colander.DateTime(default_tzinfo=None),
        # On create, mtime must be missing
        # On update, mtime is required
        'missing': colander.null,
        'title': 'Edited At',
        'widget': None,
        'colModel': {
            'width': 130,
            'editable': False
        }
    },
    'owner_display_name': {
        'type': colander.String(),
        'missing': colander.null,
        'title': 'Owner',
        'widget': None,
        'colModel': {
            'width': 100,
            'editable': False
        }
    },
    'editor_display_name': {
        'type': colander.String(),
        'missing': colander.null,
        'title': 'Editor',
        'widget': None,
        'colModel': {
            'width': 100,
            'editable': False
        }
    }
}


class DefaultMixin(object):
    """Mixin to add Parenchym's standard fields to a model class.

    These are: id, ctime, owner, mtime, editor.
    """

    id = Column(Integer, primary_key=True, nullable=False)
    """Primary key of table."""

    ctime = Column(DateTime, server_default=func.current_timestamp(),
        nullable=False)
    """Timestamp, creation time."""

    FIND_ONE_FIELD = None

    @declared_attr
    def owner(cls):
        """ID of user who created this record."""
        return Column(Integer,
            ForeignKey("principal.id", onupdate="CASCADE",
                ondelete="RESTRICT"),
            nullable=False)

    mtime = Column(DateTime, onupdate=func.current_timestamp(), nullable=True)
    """Timestamp, last edit time."""

    @declared_attr
    def editor(cls):
        """ID of user who was last editor."""
        return Column(Integer,
            ForeignKey("principal.id", onupdate="CASCADE",
                ondelete="RESTRICT"),
            nullable=True, onupdate=_get_current_user)

    def dump(self):
        from pysite.models import todict
        from pprint import pprint
        pprint(todict(self))

    @classmethod
    def find_one(cls, criterion):
        """
        Some entities have besides the PK column another one that is unique and
        thus can identify the entity. :meth:`find_one()` allows to load such an
        entity by giving as ``criterion`` either the PK value (int) or a value
        from that unique column (e.g. a str).

        Since each model may have a different unique column,
        :attr:`FIND_ONE_FIELD` denotes the name of that column. It is None if
        that model has no unique column besides the PK.

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

###@event.listens_for(sqlalchemy.engine.Engine, "before_cursor_execute", retval=True)
###def before_cursor_execute(conn, cursor, statement,
###                parameters, context, executemany):
###    print("\n", 'v'*79)
###    print(sqlparse.format(statement, reindent=True, keyword_case='upper'))
###    print('^'*79, "\n")
###    return statement, parameters


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
###     ``sqlalchemy.exc.InvalidRequestError: No such event 'connect' for
###     target 'None'``
###     """
###     cursor = dbapi_connection.cursor()
###     cursor.execute("PRAGMA foreign_keys=ON")
###     cursor.close()
### # ================================


# ===[ HELPER ]===================

def todict(o, fully_qualified=False, fmap=None):
    """Transmogrifies data of record object into dict.

    Inspired by
    http://blog.mitechie.com/2010/04/01/hacking-the-sqlalchemy-base-class/
    Converts only physical table columns. Columns created by e.g.
    relationship() must be handled otherwise.

    :param o: Data to transmogrify
    :param fully_qualified: Whether dict keys should be fully qualified (schema
        + '.' + table + '.' + column) or not (just column name). *CAVEAT* Full
        qualification is only possible if ``o`` has attribute ``__table__``.
        E.g. a KeyedTiuple does not.
    :param fmap: Mapping of field names to functions. Each function is called to
        build the value for this field.

    :rtype: Dict
    """
    def convert_datetime(value):
        try:
            return value.strftime("%Y-%m-%d %H:%M:%S")
        except AttributeError:
            # 'NoneType' object has no attribute 'strftime'
            return None

    d = {}
    if isinstance(o, sqlalchemy.util.KeyedTuple):
        d = o._asdict()
    else:
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

    if fmap:
        for k, func in fmap.items():
            d[k] = func(o)
    return d


def todata(rs, fully_qualified=False, fmap=None):
    """Transmogrifies a result set into a list of dicts.

    If ``rs`` is a single instance, only a dict is returned. If ``rs`` is a
    list, a list of dicts is returned.

    :param rs: Data to transmogrify
    :param fully_qualified: Whether dict keys should be fully qualified (schema
        + '.' + table + '.' + column) or not (just column name)

    :rtype: Dict or list of dicts
    """
    if isinstance(rs, (list, sqlalchemy.orm.query.Query)):
        data = []
        for row in rs:
            data.append(todict(row, fully_qualified=fully_qualified, fmap=fmap))
        return data
    else:
        return todict(rs, fully_qualified=fully_qualified, fmap=fmap)


def attribute_names(cls, kind="all"):
    if kind == 'columnproperty':
        return [prop.key for prop in class_mapper(cls).iterate_properties
            if isinstance(prop, ColumnProperty)]
    else:
        return [prop.key for prop in class_mapper(cls).iterate_properties]


# ===[ COMPILER CREATEVIEW ]=======

# http://stackoverflow.com/questions/9766940/how-to-create-an-sql-view-with-sqlalchemy

class CreateView(Executable, ClauseElement):
    def __init__(self, name, select):
        self.name = name
        self.select = select


@compiles(CreateView)
def visit_create_view(element, compiler, **kw):
    return "CREATE VIEW %s AS %s" % (
         element.name,
         compiler.process(element.select, literal_binds=True)
         )

# # test data
# from sqlalchemy import MetaData, Column, Integer
# from sqlalchemy.engine import create_engine
# engine = create_engine('sqlite://')
# metadata = MetaData(engine)
# t = Table('t',
#           metadata,
#           Column('id', Integer, primary_key=True),
#           Column('number', Integer))
# t.create()
# engine.execute(t.insert().values(id=1, number=3))
# engine.execute(t.insert().values(id=9, number=-3))
#
# # create view
# createview = CreateView('viewname', t.select().where(t.c.id>5))
# engine.execute(createview)
#
# # reflect view and print result
# v = Table('viewname', metadata, autoload=True)
# for r in engine.execute(v.select()):
#     print r
#
# @compiles(CreateView, 'sqlite')
# def visit_create_view(element, compiler, **kw):
#     return "CREATE VIEW IF NOT EXISTS %s AS %s" % (
#          element.name,
#          compiler.process(element.select, literal_binds=True)
#          )
