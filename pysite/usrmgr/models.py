# -*- coding: utf-8 -*-

import datetime
from sqlalchemy import *
#from sqlalchemy import event
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.sql import and_
from sqlalchemy.orm import relationship
from sqlalchemy.orm import validates
from sqlalchemy.orm.exc import NoResultFound


from pysite.models import DbSession, DbBase, DefaultMixin

__all__ = ['Principal', 'Role', 'RoleMember']


class RoleMember(DbBase, DefaultMixin):
    __tablename__ = "rolemember"
    __table_args__ = (
        UniqueConstraint('role_id', 'principal_id'),
        {
            #'schema': 'pym'
        }
    )

    principal_id = Column(BigInteger,
            #ForeignKey("pym.principal.id", onupdate="CASCADE", ondelete="CASCADE"),
            ForeignKey("principal.id", onupdate="CASCADE", ondelete="CASCADE"),
            nullable=False)
    role_id = Column(BigInteger,
            #ForeignKey("pym.role.id", onupdate="CASCADE", ondelete="CASCADE"),
            ForeignKey("role.id", onupdate="CASCADE", ondelete="CASCADE"),
            nullable=False)
###    role = relationship('Role', backref=backref('role_members', cascade="all,delete,delete-orphan") )
###    principal = relationship('Principal', 
###        primaryjoin='Principal.id==RoleMember.principal_id',
###        backref=backref('role_members', cascade="all,delete,delete-orphan") )

    def __str__(self):
        return "<RoleMember(id={0}, role_id='{1}', principal_id='{2}'>".format(
            self.id, self.role_id, self.principal_id)


def default_display_name(context):
    """Build default value for ``display_name``."""
    s = ''
###    print "*****"
###    print dir(context)
###    print "----------"
###    print dir(context.compiled_parameters)
###    print context.compiled_parameters
###    print "*****"
    # For INSERT we have current_parameters, because form fills these.
    # For UPDATE we may have them not (KeyError). Where can we access the loaded attributes?
    fn = context.current_parameters['first_name']
    ln = context.current_parameters['last_name']
    a = []
    try:
        if len(fn) > 0: a.append(fn)
    except TypeError: # If fn is None
        pass
    try:
        if len(ln) > 0: a.append(ln)
    except TypeError: # If ln is None
        pass
    if len(a) == 0:
        s = context.current_parameters['principal']
    else:
        s = " ".join(a)
    return s

def default_principal(context):
    """Builds default value for principal."""
    s = ''
    # For INSERT we have current_parameters, because form fills these.
    # For UPDATE we may have them not (KeyError). Where can we access the loaded attributes?
    fn = context.current_parameters['first_name'].lower()
    ln = context.current_parameters['last_name'].lower()
    a = []
    try:
        if len(fn) > 0: a.append(fn)
    except TypeError: # If fn is None
        pass
    try:
        if len(ln) > 0: a.append(ln)
    except TypeError: # If ln is None
        pass
    if a:
        s = '.'.join(a)
    else:
        s = context.current_parameters['email']
    return s

class Principal(DbBase, DefaultMixin):
    """Principals (users).

    Principal must be unique. We store the string as-is, but treat it as
    lowercase: 'FOO' == 'foo' --> True.
    Since SQLAlchemy does not support PostgreSQL's functional indexes, we 
    create such an index manually when the principal table is created.

    Emails are automatically lowercased. Emails must be unique.
    
    TODO  Encrypt password
    """
    __tablename__ = "principal"
    __table_args__ = (
        {
            #'schema': 'pym'
        }
    )

    is_enabled      = Column(Boolean, nullable=False, default=False)
    """Tells whether or not a (human) admin has en/disabled this account."""
    is_blocked      = Column(Boolean, nullable=False, default=False)
    """Tells whether or not some automated process has en/disabled this account."""
    principal       = Column(Unicode(255), nullable=False, index=True,
                        default=default_principal)
    """Principal or user name"""
    pwd             = Column(Unicode(32))
    """Password"""
    identity_url    = Column(Unicode(255), index=True, unique=True)
    """Used for login by OpenID"""
    email           = Column(Unicode(128), nullable=False, unique=True)
    """Email address. Always lowecased."""
    first_name      = Column(Unicode(64))
    """User's first name"""
    last_name       = Column(Unicode(64))
    """User's last name"""
    display_name    = Column(Unicode(255), unique=True, default=default_display_name)
    """User is displayed like this. Usually 'first_name last_name' or 'principal'"""
    login_time      = Column(DateTime)
    """Timestamp of current login"""
    prev_login_time = Column(DateTime)
    """Timestamp of previous login"""
    gui_token       = Column(String(36), index=True, unique=True)
    """Hmmm...?"""
    notes           = Column(UnicodeText)
    """Well, some notes."""
    # XXX Too bad: we cannot simply do roles.append(new_role), because
    #     when SA saves the modified principal, it just sets values for
    #     principal_id and role_id, not owner which is required:
    #     IntegrityError: (IntegrityError) null value in column "owner"
    #         violates not-null constraint
    #             'INSERT INTO pym.rolemember (principal_id, role_id) VALUES
    #             (%(principal_id)s, %(role_id)s) RETURNING pym.rolemember.id'
    #             {'principal_id': 2L, 'role_id': 101L}
    roles = relationship('Role', secondary=RoleMember.__table__,
        primaryjoin='Principal.id==RoleMember.principal_id',
        backref="principals"
    )
    role_names = association_proxy('roles', 'name')

    @validates('email')
    def validate_email(self, key, email):
        if email is None:
            return email
        assert '@' in email
        return email.lower()
    
    @classmethod
    def load_by_principal(cls, principal):
        """Loads a user by principal.

        This class method is provided for use in :class:`pym.security.user` to
        load user's data during login. If we have several authentication
        backends, each backend must implement this method to abide by a certain
        interface.
        """
        sess = DbSession()
        try:
            p = sess.query(cls).filter(cls.principal==principal).one()
        except NoResultFound:
            raise LookupError('User not found')
        return p
    
    @classmethod
    def _login(cls, filter):
        """Performs login.

        Called by the ``login_by...`` methods which initialise the filter.
        """
        filter.append(cls.is_enabled == True)
        filter.append(cls.is_blocked == False)
        # What's the difference of using the session like here:
        #   sess = DbSession()
        # and using DbSession.query directly, like done in load()
        # (as seen in other apps)?
        sess = DbSession()
        try:
            p = sess.query(cls).filter(and_(*filter)).one()
        except NoResultFound:
            raise LookupError('User not found')
        p.prev_login_time = p.login_time
        p.login_time = datetime.datetime.now()
        sess.flush()
        return p

    @classmethod
    def _check_credentials(*args):
        """Ensure that given credentials are not empty.

        This ensures that login fails with empty password or empty
        identity URL.
        """
        for a in args:
            if a is None or a == '' or a is b'':
                raise LookupError('Invalid credentials')

    @classmethod
    def login_by_principal(cls, principal, pwd):
        """Logs user in by principal and password, returns principal instance.

        Raises exception ``LookupError`` if user is not found.
        """
        Principal._check_credentials(principal, pwd)
        filter = []
        filter.append(cls.principal == principal)
        filter.append(cls.pwd == pwd)
        return Principal._login(filter)

    @classmethod
    def login_by_email(cls, email, pwd):
        """Logs user in by email and password, returns principal instance.

        Raises exception ``LookupError`` if user is not found.
        """
        Principal._check_credentials(email, pwd)
        filter = []
        filter.append(cls.email == email)
        filter.append(cls.pwd == pwd)
        return Principal._login(filter)

    @classmethod
    def login_by_identity_url(cls, identity_url):
        """Logs user in by identity URL (OpenID), returns principal instance.

        Raises exception ``LookupError`` if user is not found.
        """
        Principal._check_credentials(identity_url)
        filter = []
        filter.append(cls.identity_url == identity_url)
        return Principal._login(filter)
    
    @classmethod
    def logout(cls, uid):
        """Performs logout.
        """
        pass

    def __str__(self):
        return "<Principal(id={0}, principal='{1}', email='{2}'>".format(
            self.id, self.principal, self.email)


### # XXX This is PostgreSQL only!
### def principal_after_create(target, conn, **kw):
###     """Creates functional unique index on 'lower(principal)'.
### 
###     """
###     conn.execute(
###         "CREATE UNIQUE INDEX uxlc_principal_principal ON pym.principal(lower(principal))"
###     )
### 
### event.listen(Principal.__table__, "after_create", principal_after_create)


class Role(DbBase, DefaultMixin):
    __tablename__  = "role"
    __table_args__ = (
        {
            #'schema': 'pym'
        }
    )

    name           = Column(Unicode(255), nullable=False, index=True, unique=True)
    notes          = Column(Unicode(255))

    def __str__(self):
        return "<Role(id={0}, name='{1}'>".format(
            self.id, self.name)


